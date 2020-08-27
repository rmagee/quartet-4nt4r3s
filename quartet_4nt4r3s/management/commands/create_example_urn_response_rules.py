from quartet_4nt4r3s.management.commands import utils
from django.core.management import base

class Command(base.BaseCommand):
    help = 'Creates the response rules for internal ' \
           'and external sources to receive GTINs as URNs.'

    def handle(self, *args, **options):
        print('Creating the response rule...')
        utils.create_rfxcel_gtin_response_rule()
        print('Complete...creating the response template...')
        utils.create_rfxcel_template()
        print('Complete...creating the sequential rule')
        utils.create_sequential_rfxcel_gtin_response_rule()
        print('Complete...creating the sequential sscc rule')
        utils.create_sequential_rfxcel_sscc_response_rule()
