# Django-Hattori

Command to anonymize sensitive data. This app helps you anonymize data in a database used for development of a Django project.

This app is based on [Django-Database-Anonymizer](https://github.com/Blueshoe/Django-Database-Anonymizer), using [Faker](https://github.com/joke2k/faker) to anonymize the values.

## Installation

Install using pip:

```
pip install django-hattori
```

Then add ``'hattori'`` to your ``INSTALLED_APPS``.

```
INSTALLED_APPS = [
    ...
    'hattori',
]
```

### Important

***You should only run the anonymize process in PRE or development environments***. To avoid problems by default anonymization is disabled.

To enable you must add to settings ```ANONYMIZE_ENABLED=True```


## Usage

How to execute command:

    ./manage.py anonymize_db

Possible arguments:

* ```-a, --app```: Define a app you want to anonymize. All anonymizers in this app will be run. Eg. ```anonymize_db -a shop```
* ```-m, --models```: List of models you want to anonymize. Eg. ```anonymize_db -m Customer,Product```
* ```-b, --batch-size```: batch size used in the bulk_update of the instances. Depends on the DB machine, default use 500.


## Writing anonymizers

In order to use the management command we need to define _**anonymizers**_.

* Create a module _anonymizers.py_ in the given django-app
* An _anonymizer_ is a simple class that inherits from ```BaseAnonymizer```
* Each anonymizer class is going to represent **one** model
* An anonymizer has the following members:
    * ```model```: (required) The model class for this anonymizer
    * ```attributes```: (required) List of tuples that determine which fields to replace. The first value of the tuple is the fieldname, the second value is the _**replacer**_
    * ```get_query_set()```: (optional) Define your QuerySet
* A _replacer_ is either of type _str_ or _callable_
* A callable _replacer_ is a Faker instance or custom replacer.
* All Faker methods are available. For more info read the official documentation [Faker!](http://faker.readthedocs.io/en/master/providers.html)


#### Example
```
from hattori.base import BaseAnonymizer, faker
from shop.models import Customer

class CustomerAnonymizer(BaseAnonymizer):
    model = Customer

    attributes = [
        ('card_number', faker.credit_card_number),
        ('first_name', faker.first_name),
        ('last_name', faker.last_name),
        ('phone', faker.phone_number),
        ('email', faker.email),
        ('city', faker.city),
        ('comment', faker.text),
        ('description', 'fix string'),
        ('code', faker.pystr),
    ]

    def get_query_set(self):
        return Customer.objects.filter(age__gt=18)
```

#### Extending the existing replacers with arguments
Use lambdas to extend certain predefined replacers with arguments, like `min_chars` or `max_chars` on `faker.pystr`:

```
('code', lambda **kwargs: faker.pystr(min_chars=250, max_chars=250, **kwargs)),
```

**Important**: don't forget the ****kwargs**!
