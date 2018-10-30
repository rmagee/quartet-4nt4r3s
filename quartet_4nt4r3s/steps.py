import io

from django.core.files.base import File

from quartet_epcis.parsing.steps import EPCISParsingStep as EPS
from quartet_capture.rules import RuleContext
from quartet_epcis.parsing.parser import QuartetParser

from quartet_4nt4r3s.parser import BusinessEPCISParser


class EPCISParsingStep(EPS):
    def execute(self, data, rule_context: RuleContext):
        parser_type = QuartetParser if self.loose_enforcement else BusinessEPCISParser
        self.info('Loose Enforcement of busines rules set to %s',
                  self.loose_enforcement)
        self.info('Parsing message %s.dat', rule_context.task_name)
        try:
            if isinstance(data, File):
                parser = parser_type(data)
            else:
                parser = parser_type(io.BytesIO(data))
        except TypeError:
            try:
                parser = parser_type(io.BytesIO(data.encode()))
            except AttributeError:
                self.error("Could not convert the data into a format that "
                           "could be handled.")
                raise
        parser.parse()
        self.info('Parsing complete.')
