# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2018 SerialLab Corp.  All rights reserved.
import os
import logging
from django.test import TestCase
from quartet_epcis.db_api.queries import EPCISDBProxy
from quartet_epcis.models import events, choices, headers, entries
from quartet_epcis.parsing import errors
from quartet_epcis.parsing.parser import QuartetParser
from quartet_4nt4r3s.parser import BusinessEPCISParser

db_proxy = EPCISDBProxy()
logger = logging.getLogger(__name__)

class BusinessRulesTestCase(TestCase):

    def test_business_parsing(self):
        '''
        Commissions, packs, ships and transforms.
        :return:
        '''
        # parse the xml
        self._parse_test_data()
        # check the aggregation details
        id = entries.Entry.objects.get(
            identifier='urn:epc:id:sgtin:0342195.030809.900654902111')
        decom_event = events.Event.objects.get(
            action='DELETE'
        )
        db_proxy = EPCISDBProxy()
        evs = db_proxy.get_events_by_ilmd('lotNumber', 'ABC123')
        self.assertEqual(len(evs), 1)
        self.assertEqual(len(evs[0].epc_list), 16)

    def _parse_test_data(self, test_file='data/comm-delete.xml',
                         parser_type=BusinessEPCISParser,
                         recursive_decommission=False):
        curpath = os.path.dirname(__file__)
        if isinstance(parser_type, BusinessEPCISParser):
            parser = parser_type(
                os.path.join(curpath, test_file),
                recursive_decommission=recursive_decommission
            )
        else:
            parser = parser_type(
                os.path.join(curpath, test_file),
            )
        message_id = parser.parse()
        print(parser.event_cache)
        return message_id, parser
