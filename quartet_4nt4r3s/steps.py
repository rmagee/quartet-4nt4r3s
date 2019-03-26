import io

from django.core.files.base import File

from quartet_epcis.parsing.steps import EPCISParsingStep as EPS
from quartet_capture.rules import RuleContext
from quartet_4nt4r3s.conversion import AntaresBarcodeConverter
from quartet_4nt4r3s.parser import BusinessEPCISParser
from gs123.steps import ListBarcodeConversionStep


class EPCISParsingStep(EPS):
    def execute(self, data, rule_context: RuleContext):
        increment_agg_dates = self.get_boolean_parameter(
            'Increment Aggregation Dates', True, False)
        self.info('Increment Aggregation Dates set to ', str())
        self.info('Loose Enforcement of busines rules set to %s',
                  self.loose_enforcement)
        self.info('Parsing message %s.dat', rule_context.task_name)
        try:
            if isinstance(data, File):
                parser = BusinessEPCISParser(
                    data,
                    increment_agg_dates=increment_agg_dates
                )
            else:
                parser = BusinessEPCISParser(
                    io.BytesIO(data),
                    increment_agg_dates=increment_agg_dates
                )
        except TypeError:
            try:
                parser = BusinessEPCISParser(io.BytesIO(data.encode()))
            except AttributeError:
                self.error("Could not convert the data into a format that "
                           "could be handled.")
                raise
        parser.parse()
        self.info('Parsing complete.')


class AntaresBarcodeConversionStep(ListBarcodeConversionStep):
    '''
    Allows the return of the extension digit along with serial number field.
    '''

    def convert(self, data):
        """
        Will convert the data parameter to a urn value and return.
        Override this to return a different value from the BarcodeConverter.
        :param data: The barcode value to convert.
        :return: An EPC URN based on the inbound data.
        """
        prop_val = AntaresBarcodeConverter(
            data,
            self.company_prefix_length,
            self.serial_number_length
        ).__getattribute__(self.prop_name)
        return prop_val if isinstance(prop_val, str) else prop_val()
