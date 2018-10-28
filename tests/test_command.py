# -*- encoding: utf-8 -*-

import pytest

from model_mommy import mommy
from model_mommy.recipe import seq
from tests.models import Person
from django.core.management import call_command


@pytest.mark.django_db
class TestCommand(object):

    @staticmethod
    def data(num_items=10):
        return mommy.make(Person, first_name=seq('first_name-'), last_name=seq('last_name-'), _quantity=num_items)

    def test_data_creation(self):
        self.data()
        assert Person.objects.count() == 10
        last = Person.objects.last()
        assert last.first_name == 'first_name-10'

    @pytest.mark.parametrize('num_items', [
        20000,
        40000,
    ])
    def test_simple_command(self, num_items):
        self.data(num_items=num_items)
        assert Person.objects.filter(first_name__startswith='first_name-').exists()
        call_command('anonymize_db')
        assert not Person.objects.filter(first_name__startswith='first_name-').exists()
