# This program is free software: you can redistribute it and/| modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, |
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY | FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2018 SerialLab Corp.  All rights reserved.
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from quartet_capture import models


class Command(BaseCommand):
    help = _('Creates the default rfXcel and tracelink processing rules.')

    def handle(self, *args, **options):
        if models.Rule.objects.filter(name='RFXCEL Number Request').count() == 0:
            rule = models.Rule()
            rule.name = 'RFXCEL Number Request'
            rule.description = 'Initiates Number Requests to RFXCEL systems.'
            rule.save()
            step1 = models.Step()
            step1.rule = rule
            step1.name = 'Number Request Transport Step'
            step1.description = ('Uses task data to construct a request to '
                                 'an rfXcel system.')
            step1.step_class = ('list_based_flavorpack.steps.'
                                'NumberRequestTransportStep')
            step1.order = 1
            step1.save()
            step2 = models.Step()
            step2.rule = rule
            step2.name = 'RFXCEL Parse and Write Numbers'
            step2.description = ('Parses an inbound rfXcel number response '
                                 'and saves it to file.')
            step2.step_class = ('third_party_flavors.'
                                'rfxcel_number_response_step.'
                                'RFXCELNumberResponseParserStep')
            step2.order = 2
            step2.save()
        if not models.Rule.objects.filter(name='Tracelink Number Request').exists():
            rule2 = models.Rule()
            rule2.name = 'Tracelink Number Request'
            rule2.description = ('Requests numbers from Tracelink and writes '
                                 'them persistently for use in Number '
                                 'Range distribution.')
            rule2.save()
            step3 = models.Step()
            step3.rule = rule2
            step3.name = 'Number Request Transport Step'
            step3.description = ('Requests numbers and passes the response '
                                 'to the next step (for parsing)')
            step3.step_class = ('list_based_flavorpack.steps.'
                                'NumberRequestTransportStep')
            step3.order = 1
            step3.save()
            step4 = models.Step()
            step4.rule = rule2
            step4.name = 'Tracelink Number Reponse Parser'
            step4.description = ('Parses numbers from Tracelink and writes '
                                 'them persistently for use in Number '
                                 'Range module')
            step4.step_class = ('third_party_flavors.'
                                'tracelink_number_response_step.'
                                'TracelinkNumberResponseParserStep')
            step4.order = 2
            step4.save()
