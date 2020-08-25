
import os
from django.db.utils import IntegrityError
from django.utils.translation import gettext as _

from quartet_capture.models import Rule, StepParameter, Step
from quartet_masterdata.models import TradeItem, Company
from quartet_output.models import EndPoint, EPCISOutputCriteria, \
    AuthenticationInfo
from quartet_templates.models import Template
from random_flavorpack import models
from serialbox.models import Pool, ResponseRule
from serialbox.models import SequentialRegion

template_data = """
<ns5:syncAllocateTraceIdsResponse xmlns="http://xmlns.rfxcel.com/traceability/api/3" xmlns:ns10="http://xmlns.rfxcel.com/traceability/QueryTraceIdDetailService/1" xmlns:ns2="http://xmlns.rfxcel.com/traceability/3" xmlns:ns3="http://www.w3.org/2004/11/xmlmime" xmlns:ns4="http://xmlns.rfxcel.com/traceability/messagingService/3" xmlns:ns5="http://xmlns.rfxcel.com/traceability/serializationService/3" xmlns:ns6="http://xmlns.rfxcel.com/traceability/identifier/3" xmlns:ns7="http://xmlns.rfxcel.com/traceability/serializationQueryService/3" xmlns:ns8="http://xmlns.rfxcel.com/traceability/QueryLotSummaryService/1" xmlns:ns9="http://xmlns.rfxcel.com/traceability/QuerySimpleEpcListService/1" contentStructVer="3.1.3" createDateTime="2017-10-17T04:56:47.062-05:00" requestId="{{ task_parameters.requestId }}" responseId="{{ UUID }}">
    <result>
        <ns2:code>1</ns2:code>
        <ns2:msg xml:lang="en">SUCCESS</ns2:msg>
    </result>
    <ns5:sysEventId>{{ epoch | int}}</ns5:sysEventId>
    <ns5:eventId>{{ task_parameters.eventId }}</ns5:eventId>
    <ns5:orgId qlfr="ORG_DEF">urn:epc:id:sgln:0358716.00000.0</ns5:orgId>
    <ns5:itemId qlfr="GTIN">{{ task_parameters.pool }}</ns5:itemId>
    <ns5:siteHierId qlfr="ORG_DEF">Manufacturing</ns5:siteHierId>
    <ns5:siteId qlfr="SGLN" type="LOCATION">urn:epc:id:sgln:0358716.00000.0</ns5:siteId>
    <ns5:allocIdSetCont>
        <ns6:idFormatId>JCP IDF SGTIN 12 NUM RAN</ns6:idFormatId>
        <ns6:idEncScheme>SGTIN_96</ns6:idEncScheme>
        <ns6:idGenMethod>RANDOM</ns6:idGenMethod>
        <ns6:idSetCont dataStruct="LIST">
            <ns6:idTextFormatId>PURE_ID_URI</ns6:idTextFormatId>
            <ns6:idList>
                {% for serial_number in data %}
                <ns2:id>{{serial_number}}</ns2:id>
                {% endfor %}
            </ns6:idList>
        </ns6:idSetCont>
    </ns5:allocIdSetCont>
</ns5:syncAllocateTraceIdsResponse>
"""

def create_rfxcel_gtin_response_rule():
    rule, created = Rule.objects.get_or_create(
        name='RFXCEL GTIN URN Response',
        description='A list to URN response rule.  Converts serialbox '
                    'integers to URNs.',
    )

    conversion_step, created = Step.objects.get_or_create(
        rule=rule,
        name='Integer to URN Conversion',
        step_class='quartet_integrations.serialbox.steps.ListToUrnConversionStep',
        order=1
    )
    if created:
        conversion_step.description = 'Convert the list of numbers to ' \
                                      'GTINs or SSCCs.'

    template_step, created = Step.objects.get_or_create(
        rule=rule,
        name='Render RFXCEL Reply',
        step_class='quartet_templates.steps.TemplateStep',
        order=2
    )
    if created:
        template_step.description = 'Renders the Proper RFXCEL Response'
        StepParameter.objects.create(
            name='Template Name', value='RFXCEL GTIN Response',
            step=template_step
        )


def create_rfxcel_template():
    Template.objects.get_or_create(
        name='RFXCEL GTIN Response',
        content=template_data,
        description='Format for RFXCEL Number Responses'
    )
