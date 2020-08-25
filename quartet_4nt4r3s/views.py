import requests
import logging
import uuid
from requests.auth import HTTPBasicAuth
from lxml import etree
from rest_framework.response import Response
from rest_framework import views
from rest_framework.negotiation import DefaultContentNegotiation
from list_based_flavorpack.models import ProcessingParameters
from serialbox.models import Pool
from django.contrib.auth import authenticate, login
from rest_framework import status
from django.template import loader
from django.conf import settings
from quartet_capture.tasks import create_and_queue_task, get_rules_by_filter
from quartet_capture.models import Filter

logger = logging.getLogger(__name__)


class DefaultXMLContent(DefaultContentNegotiation):

    def select_renderer(self, request, renderers, format_suffix):
        """
        Use the XML renderer as default.
        """
        # Allow URL style format override.  eg. "?format=json
        format_query_param = self.settings.URL_FORMAT_OVERRIDE
        format = format_suffix or request.query_params.get(format_query_param)
        request.query_params.get(format_query_param)
        header = request.META.get('HTTP_ACCEPT', '*/*')
        if format is None and header == '*/*':
            for renderer in renderers:
                if renderer.media_type == "application/xml":
                    return (renderer, renderer.media_type)
        return DefaultContentNegotiation.select_renderer(self, request,
                                                         renderers, format)


class AntaresAPI(views.APIView):
    """
    Base class everything Antares.
    """
    permission_classes = []

    content_negotiation_class = DefaultXMLContent

    def get_tag_text(self, root, match_string):
        try:
            return root.find(match_string).text
        except AttributeError:
            raise
        except:
            return None

    def auth_user(self, username, password):
        """
        Authenticate user.
        """
        user = authenticate(username=username, password=password)
        if user:
            return user
        else:
            return None


class AntaresNumberRequest(AntaresAPI):
    """
    Mimics:
    /rfxcelwss/services/ISerializationServiceSoapHttpPort
    Pool will be found using the itemId value:
    <ns:itemId qlfr="GTIN">[SOME.GTIN.OR.SSCC.HERE]</ns:itemId>
    if a list_based_region processing parameter with key 'item_value' and 'item_id' value is found,
    its associated pool will be used.
    Example:
    ProcessingParameter: {key: "item_value",
                          value: "10342195308095"}
    would be a match for:
    <ns:itemId qlfr="GTIN">10342195308095</ns:itemId>

    If none is found, then the itemId value is matched against the pool.machine_name.
    For instance a pool.machine_name equal to 10342195308095 would be matched if the itemId in the inbound xml
    is the following:
     <ns:itemId qlfr="GTIN">10342195308095</ns:itemId>
    """
    def post(self, request, format=None):
        root = etree.fromstring(request.body)
        scheme = getattr(settings, 'ANTARES_SERIALBOX_SCHEME', request.scheme)
        host = getattr(settings, 'ANTARES_SERIALBOX_HOST', '127.0.0.1')
        port = getattr(settings, 'ANTARES_SERIALBOX_PORT', None)
        logger.debug('Using scheme, host, port %s, %s, %s', scheme, host, port)
        header = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Header')
        body = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        username = self.get_tag_text(header, './/{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Username')
        password = self.get_tag_text(header, './/{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Password')
        id_count = self.get_tag_text(body, './/{http://xmlns.rfxcel.com/traceability/serializationService/3}idCount')
        try:
            item_id = self.get_tag_text(body, './/{http://xmlns.rfxcel.com/traceability/serializationService/3}itemId')
        except:
            item_id = self.get_tag_text(body, './/{http://xmlns.rfxcel.com/traceability/serializationService/3}allocOrgId')
            extension = self.get_tag_text(body, ".//{http://xmlns.rfxcel.com/traceability/3}val[@name='SSCC_EXT_DIGIT']")
            item_id = extension + item_id  # we need the extension in there to match different pools with the extension.
        event_id = self.get_tag_text(body, './/{http://xmlns.rfxcel.com/traceability/serializationService/3}eventId')
        pool = self.match_item_with_pool_machine_name(item_id)
        if not pool:
            # match region/pool with item_id.
            pool = self.match_item_with_param(item_id)
        payload = {'format': 'xml', 'eventId': event_id, 'requestId': event_id}
        if not port:
            url = "%s://%s/serialbox/allocate/%s/%d/?format=xml" % (
                scheme, host, pool.machine_name, int(id_count))
        else:
            url = "%s://%s:%s/serialbox/allocate/%s/%d/?format=xml" % (
                scheme, host, port, pool.machine_name, int(id_count))
        api_response = requests.get(url, params=payload, auth=HTTPBasicAuth(username, password), verify=False)
        logger.debug(api_response)

        return Response(api_response.text, api_response.status_code)

    def match_item_with_param(self, item_id):
        try:
            return ProcessingParameters.objects.get(key="item_value",
                                                    value=item_id).list_based_region.pool
        except:
            return None

    def match_item_with_pool_machine_name(self, item_id):
        return Pool.objects.get(machine_name=item_id)


class AntaresEPCISReport(AntaresAPI):
    """
    Mimics /rfxcelwss/services/IMessagingServiceSoapHttpPort
    Takes in a SOAP request with an EPCIS report,
    tosses away the SOAP piece and saves the EPCIS document to a file,
    also kicks off a rule.
    """

    def post(self, request, format=None):
        # get the message from the request
        root = etree.fromstring(request.body)
        header = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Header')
        body = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        username = self.get_tag_text(header,
                                     './/{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Username')
        password = self.get_tag_text(header,
                                     './/{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Password')
        user = self.auth_user(username=username, password=password)
        if user:
            data = {"uuid_msg_id": uuid.uuid1(),
                    "created_date_time": "2018-10-10"}
            template = loader.get_template("soap/received.xml")
            xml = template.render(data)
            run_immediately = request.query_params.get('run-immediately',
                                                       False)
            self.trigger_epcis_task(body, user, run_immediately)
            return Response(xml, status=status.HTTP_200_OK)
        else:
            template = loader.get_template("soap/unauthorized.xml")
            xml = template.render({})
            return Response(xml, status=status.HTTP_401_UNAUTHORIZED)

    def trigger_epcis_task(self, soap_body, user, run_immediately=False):
        """
        Triggers an EPCIS rule task using the EPCISDocument.
        """
        epcis_document = etree.tostring(
            soap_body.find('.//{urn:epcglobal:epcis:xsd:1}EPCISDocument'))
        if isinstance(epcis_document, bytes):
            epcis_document = epcis_document.decode('utf-8')
        try:
            default_filter = getattr(settings, 'DEFAULT_ANTARES_FILTER',
                                     'Antares')
            logger.info('Default antares filter is %s', default_filter)
            rules = get_rules_by_filter(default_filter, epcis_document)
            logger.info('Rules in filter: %', rules)
        except Filter.DoesNotExist:
            rules = [getattr(settings, 'DEFAULT_ANTARES_RULE', 'EPCIS')]
            logger.debug('No filter could be found using rule %s.', rules)

        for rule in rules:
            create_and_queue_task(data=epcis_document,
                                  rule_name=rule,
                                  task_type="Input",
                                  run_immediately=run_immediately,
                                  initial_status="WAITING",
                                  task_parameters=[],
                                  user_id=user.id)
