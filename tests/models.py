# -*- encoding: utf-8 -*-

from django.db import models


class Person(models.Model):

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Person'
        verbose_name_plural = 'Persons'

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)
