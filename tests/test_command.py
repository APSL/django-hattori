# -*- encoding: utf-8 -*-

import pytest

from model_mommy import mommy
from model_mommy.recipe import seq
from tests.models import Person
from django.core.management import call_command


@pytest.mark.django_db
class TestCommand(object):

    @pytest.fixture
    def data(self):
        return mommy.make(Person, name=seq('name-'), surname=seq('surname-'), _quantity=1000)

    def test_prova(self, data):
        assert True
        assert Person.objects.count() == 1000
        last = Person.objects.last()
        assert last.name == 'name-1000'

    # def test_simple_command(self, data):
    #     call_command('anonymize_db')
    #     assert not Person.objects.filter('name-').exists()

