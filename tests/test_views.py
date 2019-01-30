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
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
django.setup()
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import Group, User
from quartet_capture import models
from quartet_capture.rules import clone_rule
from quartet_capture.views import get_rules_by_filter
from quartet_capture.management.commands.create_capture_groups import Command

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
django.setup()

class ViewTest(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username='testuser',
                                        password='unittest',
                                        email='testuser@seriallab.local')
        Command().handle()
        oag = Group.objects.get(name='Capture Access')
        user.groups.add(oag)
        user.save()
        self.client.force_authenticate(user=user)
        self.user = user

    def test_execute_view_with_filter(self):
        self._create_filter()
        url = reverse('antares-epcis-report')
        data = self._get_test_data()
        response = self.client.post(
            '{0}?filter=utf&run-immediately=true'.format(url),
            data=data, content_type='text')
        self.assertEqual(response.status_code, 200)
        self.assertIn('RECEIVED', response.data)

    def test_execute_view_with_rule(self):
        self._create_filter(filter_name='idonotexist')
        url = reverse('antares-epcis-report')
        data = self._get_test_data()
        response = self.client.post(
            '{0}?filter=utf&run-immediately=true'.format(url),
            {'file': data},
            format='multipart')
        self.assertEqual(response.status_code, 200)
        self.assertIn('RECEIVED', response.data)

    def _get_test_data(self):
        '''
        Loads the XML file and passes its data back as a string.
        '''
        curpath = os.path.dirname(__file__)
        data_path = os.path.join(curpath, 'data/antares-lot-batch.xml')
        with open(data_path) as data_file:
            return data_file.read()

    def _create_rule(self, rule_name='epcis'):
        db_rule = models.Rule()
        db_rule.name = rule_name
        db_rule.description = 'EPCIS Parsing rule utilizing antares parser.'
        db_rule.save()
        rp = models.RuleParameter(name='test name', value='test value',
                                  rule=db_rule)
        rp.save()
        # create a new step
        epcis_step = models.Step()
        epcis_step.name = 'parse-epcis'
        epcis_step.description = 'Parse the EPCIS data and store in database.'
        epcis_step.order = 1
        epcis_step.step_class = 'quartet_4nt4r3s.steps.EPCISParsingStep'
        epcis_step.rule = db_rule
        epcis_step.save()
        return db_rule

    def _create_filter(self, filter_name='Antares', rule=None):
        rule = rule or self._create_rule()
        rule_2 = self._create_rule('epcis_2')
        rule_3 = self._create_rule('epcis_3')
        filter = models.Filter.objects.create(name=filter_name,
                                              description='unit testing')
        rule_filter_1 = models.RuleFilter.objects.create(
            filter=filter,
            rule=rule,
            search_value='^<asdfasdfasdf',
            search_type='regex',
            order=1,
            reverse=False
        )
        rule_filter_2 = models.RuleFilter.objects.create(
            filter=filter,
            rule=rule_2,
            search_value='urn:epc:id:sgtin:0368220',
            search_type='search',
            order=2,
            break_on_true=True,
            reverse=False
        )
        rule_filter_3 = models.RuleFilter.objects.create(
            filter=filter,
            rule=rule_3,
            search_value='///////',
            search_type='search',
            order=3,
            reverse=False,
            default=True
        )
        return filter, rule_filter_1, rule_filter_2, rule_filter_3
