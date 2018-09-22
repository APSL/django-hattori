# -*- coding: utf-8 -*-

import logging
import concurrent.futures

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

    model = None
    attributes = None

    def __init__(self):
        if not self.model or not self.attributes:
            logger.info('ERROR: Your anonymizer is missing the model or attributes definition!')
            exit(1)

    def get_query_set(self):
        """
        You can override this in your Anonymizer.
        :return: QuerySet
        """
        return self.model.objects.all()

    @staticmethod
    def _get_allowed_value(replacer, model_instance, field_name):
        retval = replacer()
        max_length = model_instance._meta.get_field(field_name).max_length
        if max_length:
            retval = retval[:max_length]
        return retval

    def run(self, batch_size, max_workers):
        instances = self.get_query_set()
        instances_processed, count_instances, count_fields = self._process_instances(instances, max_workers)
        bulk_update(instances_processed, update_fields=[attrs[0] for attrs in self.attributes], batch_size=batch_size)
        return len(self.attributes), count_instances, count_fields

    def _process_instances(self, instances, max_workers):
        count_fields, count_instances, errors = 0, 0, 0
        progress_bar = tqdm(desc="Processing", total=instances.count())
        # enqueuing instances
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_ref = {
                executor.submit(self._process_instance, instance): instance for instance in instances
            }
        # processing results
        for future in concurrent.futures.as_completed(future_ref):
            try:
                model_instance, num_fields = future.result()
            except Exception:
                errors += 1
            else:
                # model_instance.save()
                count_fields += num_fields
                count_instances += 1
            progress_bar.update(1)
        progress_bar.close()
        return instances, count_instances, count_fields

    def _process_instance(self, model_instance):
        count_fields = 0
        for field_name, replacer in self.attributes:
            if callable(replacer):
                replaced_value = self._get_allowed_value(replacer, model_instance, field_name)
            elif isinstance(replacer, string_types):
                replaced_value = replacer
            else:
                raise TypeError('Replacers need to be callables or Strings!')
            setattr(model_instance, field_name, replaced_value)
            count_fields += 1

        return model_instance, count_fields
