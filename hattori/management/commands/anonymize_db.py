# -*- coding: utf-8 -*-
from django.core.management import BaseCommand

from hattori import constants
from hattori.constants import ANONYMIZER_MODULE_NAME
from hattori.exceptions import HattoriException
from hattori.utils import setting, autodiscover_module, get_app_anonymizers


class Command(BaseCommand):
    help = 'This command anonymize real (user-)data of model instances in your database with mock data.'
    modules = None  # List of anonymizers modules. They can be placed in every app
    anonymize_enabled = setting('ANONYMIZE_ENABLED', False)

    def add_arguments(self, parser):
        parser.add_argument(
            '-a',
            '--app',
            help='Only anonymize the given app',
            dest="app",
            metavar="APP"
        )
        parser.add_argument(
            "-m",
            "--model",
            "--models",
            dest="models",
            help="Models to anonymize. Separate multiples by comma.",
            metavar="MODEL"
        )
        parser.add_argument(
            "-b",
            "--batch-size",
            dest="batch_size",
            help="batch size used in the bulk_update of the instances. Depends on the DB machine, defaults use 500.",
            metavar="BATCH_SIZE",
            type=int,
            default=constants.DEFAULT_CHUNK_SIZE,
        )

    def handle(self, *args, **options):
        if not self.anonymize_enabled:
            self.stdout.write(self.style.WARNING('You must set ANONYMIZE_ENABLED to True'))
            exit()

        try:
            modules = autodiscover_module(ANONYMIZER_MODULE_NAME, app_name=options.get('app'))
        except HattoriException as e:
            self.stdout.write(self.style.ERROR(e))
            exit(1)

        total_replacements_count = 0

        for module in modules:
            anonymizers = get_app_anonymizers(module, selected_models=options.get('models'))

            if len(anonymizers) == 0:
                continue

            for anonymizer_class_name in anonymizers:
                anonymizer = getattr(module, anonymizer_class_name)()
                # Start the anonymizing process
                self.stdout.write('{}.{}:'.format(module.__package__, anonymizer.model.__name__))
                number_of_replaced_fields = anonymizer.run(options.get('batch_size'))
                self.stdout.write('- {} fields, {} model instances, {} total replacements'.format(
                    number_of_replaced_fields[0],
                    number_of_replaced_fields[1],
                    number_of_replaced_fields[2]
                ))
                total_replacements_count += number_of_replaced_fields[2]
        self.stdout.write(self.style.SUCCESS('DONE. Replaced {} values in total'.format(total_replacements_count)))
