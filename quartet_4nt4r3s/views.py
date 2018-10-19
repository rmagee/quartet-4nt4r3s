import requests
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
from quartet_capture.tasks import create_and_queue_task


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
        return DefaultContentNegotiation.select_renderer(self, request, renderers, format)


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
        user = authenticate(username = username, password = password)
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
        header = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Header')
        body = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        username = self.get_tag_text(header, './/{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Username')
        password = self.get_tag_text(header, './/{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Password')
        id_count = self.get_tag_text(body, './/{http://xmlns.rfxcel.com/traceability/serializationService/3}idCount')
        item_id = self.get_tag_text(body, './/{http://xmlns.rfxcel.com/traceability/serializationService/3}itemId')
        # match region/pool with item_id.
        pool = self.match_item_with_param(item_id)
        if not pool:
            pool = self.match_item_with_pool_machine_name(item_id)
        url = "%s://%s/serialbox/allocate/%s/%d/?format=xml" % (request.scheme, request.get_host(), pool.machine_name, int(id_count))
        api_response = requests.get(url, auth=HTTPBasicAuth(username, password))
        return Response(api_response.text, api_response.status_code)
    
    def match_item_with_param(self, item_id):
        try:
            return ProcessingParameters.objects.get(key="item_value", value=item_id).list_based_region.pool
        except:
            return None

    def match_item_with_pool_machine_name(self, item_id):
        try:
            return Pool.objects.get(machine_name=item_id)
        except:
            return None


class AntaresEPCISReport(AntaresAPI):
    """
    Mimics /rfxcelwss/services/IMessagingServiceSoapHttpPort
    Takes in a SOAP request with an EPCIS report,
    tosses away the SOAP piece and saves the EPCIS document to a file,
    also kicks off a rule.
    """

    def post(self, request, format=None):
        root = etree.fromstring(request.body)
        header = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Header')
        body = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        username = self.get_tag_text(header, './/{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Username')
        password = self.get_tag_text(header, './/{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Password')
        user = self.auth_user(username = username, password = password)
        if user:
            data = {"uuid_msg_id": uuid.uuid1(), "created_date_time": "2018-10-10"}
            template = loader.get_template("soap/received.xml")
            xml = template.render(data)
            self.trigger_epcis_task(body, user)
            return Response(xml, status=status.HTTP_200_OK)
        else:
            template = loader.get_template("soap/unauthorized.xml")
            xml = template.render({})
            return Response(xml, status=status.HTTP_401_UNAUTHORIZED)
    
    def trigger_epcis_task(self, soap_body, user):
        """
        Triggers an EPCIS rule task using the EPCISDocument.
        """
        epcis_document = etree.tostring(soap_body.find('.//{urn:epcglobal:epcis:xsd:1}EPCISDocument'))
        task = create_and_queue_task(data=epcis_document,
                                     rule_name="EPCIS",
                                     task_type="Input",
                                     run_immediately=False,
                                     initial_status="WAITING",
                                     task_parameters=[],
                                     user_id=user.id)
