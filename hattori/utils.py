# -*- coding: utf-8 -*-
import inspect
import logging
from importlib import import_module

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from hattori.base import BaseAnonymizer
from hattori.exceptions import HattoriException

logger = logging.getLogger(__name__)


def setting(name, default=None, strict=False):
    """
    Helper function to get a Django setting by name. If setting doesn't exists
    it can return a default or raise an error if in strict mode.

    :param name: Name of setting
    :type name: str
    :param default: Value if setting is unfound
    :param strict: Define if return default value or raise an error
    :type strict: bool
    :returns: Setting's value
    :raises: django.core.exceptions.ImproperlyConfigured if setting is unfound
             and strict mode
    """
    if strict and not hasattr(settings, name):
        msg = "You must provide settings.%s" % name
        raise ImproperlyConfigured(msg)
    return getattr(settings, name, default)


def autodiscover_module(module_name, app_name=None):
    logger.info('Autodiscovering anonymizers modules ...')
    apps_to_search = [app_name] if app_name else settings.INSTALLED_APPS
    modules = []
    for app in apps_to_search:
        try:
            import_module(app)
        except ImportError as e:
            raise HattoriException('ERROR: Can not find app {}'.format(app), e)
        try:
            modules.append(import_module('%s.%s' % (app, module_name)))
        except ImportError as e:
            if app_name:
                raise HattoriException('ERROR: Can not find module {}'.format(module_name, app), e)
    logger.info('Found anonymizers for {} apps'.format(len(modules)))
    return modules


def get_app_anonymizers(module, selected_models=None):
    logger.info('Autodiscovering Anonymizer classes from {} module...'.format(module.__package__))
    models = None
    if selected_models is not None:
        models = [m.strip() for m in selected_models.split(',')]

    if models:
        clazzes = [m[0] for m in inspect.getmembers(module, inspect.isclass)
                   if BaseAnonymizer in m[1].__bases__ and m[1].model.__name__ in models]
    else:
        clazzes = [m[0] for m in inspect.getmembers(module, inspect.isclass) if BaseAnonymizer in m[1].__bases__]
    if len(clazzes) == 0:
        logger.info('Not found any Anonymizer class from {} module'.format(module.__package__))
    return clazzes
