import copy
from datetime import timedelta
from dateutil import parser
from pytz import timezone
from EPCPyYes.core.v1_2 import events, events as yes_events
from EPCPyYes.core.v1_2.CBV import business_steps, dispositions
from quartet_epcis.parsing.business_parser import BusinessEPCISParser as BEP


class BusinessEPCISParser(BEP):

    def __init__(self, stream, event_cache_size: int = 1024,
                 recursive_decommission: bool = True,
                 increment_agg_dates=True, increment_val=1):
        """
        The antares parser does some special things to overcome some weirdness
        in the antares epcis support.  During DELETE events for example, the
        parser will first commission epcs before deleting them since the
        antares system never sends commission events for decommissioned epcs.
        In addition, the antares system will also aggregate all levels using
        the same timestamp which causes all kinds of problems with other
        systems.  This parser will increment each commissioning event timestamp
        by one second as they are parsed to make up for this.
        :param stream:  See BusinessEPCParser docs.
        :param event_cache_size:  See BusinessEPCParser docs.
        :param recursive_decommission: See BusinessEPCParser docs.
        :param increment_agg_dates: Whether or not to increase the dates.
        :param increment_val: The amount to increment each aggregation
        event time date in seconds.
        """
        super().__init__(stream, event_cache_size, recursive_decommission)
        self.increment_agg_dates = increment_agg_dates
        self.increment_val = increment_val

    def handle_object_event(self, epcis_event: yes_events.ObjectEvent):
        if epcis_event.action == events.Action.delete.value:
            self._pre_commission_event(epcis_event)
        super().handle_object_event(epcis_event)

    def handle_aggregation_event(self, epcis_event: events.AggregationEvent):
        self.convert_dates(epcis_event, self.increment_agg_dates,
                           self.increment_val)
        super().handle_aggregation_event(epcis_event)

    def _pre_commission_event(self, epcis_event: yes_events.ObjectEvent):
        oe = copy.copy(epcis_event)
        oe.action = events.Action.add.value
        oe.biz_step = business_steps.BusinessSteps.commissioning.value
        oe.disposition = dispositions.Disposition.active
        self.handle_object_event(oe)

    def format_datetime(self, dt_string, increment_dates=False,
                        increment_val=0):
        try:
            dt_obj = parser.parse(dt_string).astimezone(timezone('UTC'))
            if increment_dates:
                dt_obj = dt_obj + timedelta(seconds=increment_val)
            return dt_obj.strftime('%Y-%m-%dT%H:%M:%SZ')
        except:
            return dt_string

    def convert_dates(self, event, increment_dates=False, increment_val=0):
        if event.event_time.endswith(
            '+00:00') and event.event_timezone_offset != '+00:00':
            converted_dt_string = re.sub(r"\+00:00$",
                                         event.event_timezone_offset,
                                         event.event_time)
            event.event_time = self.format_datetime(
                converted_dt_string, increment_dates, increment_val)
        else:
            event.event_time = self.format_datetime(event.event_time,
                                                    increment_dates,
                                                    increment_val)
        if event.record_time:
            event.record_time = self.format_datetime(event.record_time,
                                                     increment_dates,
                                                     increment_val)
