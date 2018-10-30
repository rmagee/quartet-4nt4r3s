import copy

from EPCPyYes.core.v1_2 import events, events as yes_events
from EPCPyYes.core.v1_2.CBV import business_steps, dispositions
from quartet_epcis.models import events as db_events, choices
from quartet_epcis.parsing.business_parser import BusinessEPCISParser as BEP, \
    EntryList


class BusinessEPCISParser(BEP):

    def handle_object_event(self, epcis_event: yes_events.ObjectEvent):
        if epcis_event.action == events.Action.delete.value:
            self._pre_commission_event(epcis_event)
        super().handle_object_event(epcis_event)

    def _pre_commission_event(self, epcis_event: yes_events.ObjectEvent):
        oe = copy.copy(epcis_event)
        oe.action = events.Action.add.value
        oe.biz_step = business_steps.BusinessSteps.commissioning.value
        oe.disposition = dispositions.Disposition.active
        self.handle_object_event(oe)
