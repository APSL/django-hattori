# -*- coding: utf-8 -*-
import logging

from tqdm import tqdm
from six import string_types
from django.conf import settings
from bulk_update.helper import bulk_update
from faker import Faker

logger = logging.getLogger(__name__)

try:
    faker = Faker(settings.LANGUAGE_CODE)
except AttributeError:
    faker = Faker()


class BaseAnonymizer:

    def __init__(self):
        try:
            getattr(self, 'model')
            getattr(self, 'attributes')
        except AttributeError:
            logger.info('ERROR: Your anonymizer is missing the model or attributes definition!')
            exit(1)

    def get_query_set(self):
        """
        You can override this in your Anonymizer.
        :return: QuerySet
        """
        return self.model.objects.all()

    def get_allowed_value(self, replacer, model_instance, field_name):
        retval = replacer()
        max_length = model_instance._meta.get_field(field_name).max_length
        if max_length:
            retval = retval[:max_length]
        return retval

    def _process_instances(self, instances):
        count_fields = 0
        count_instances = 0

        progress_bar = tqdm(desc="Processing", total=instances.count())
        for model_instance in instances:
            for field_name, replacer in self.attributes:
                if callable(replacer):
                    replaced_value = self.get_allowed_value(replacer, model_instance, field_name)
                elif isinstance(replacer, string_types):
                    replaced_value = replacer
                else:
                    raise TypeError('Replacers need to be callables or Strings!')
                setattr(model_instance, field_name, replaced_value)
                count_fields += 1
            count_instances += 1
            progress_bar.update(1)
        progress_bar.close()
        return instances, count_instances, count_fields

    def run(self, batch_size):
        instances = self.get_query_set()

        instances_processed, count_instances, count_fields = self._process_instances(instances)

        bulk_update(instances_processed, update_fields=[attrs[0] for attrs in self.attributes],
                    batch_size=batch_size)

        return len(self.attributes), count_instances, count_fields
