# -*- encoding: utf-8 -*-
from django.db import models


class Person(models.Model):

    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Person'
        verbose_name_plural = 'Persons'

    def __str__(self):
        return '{} {}'.format(self.name, self.surname)
