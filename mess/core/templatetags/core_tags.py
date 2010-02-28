import re
from django import template

register = template.Library()

@register.filter
def match(value, regex):
    """
    Tests a regular expression against the start of a value.

    Especially useful in if statements::

        {% if value|match:"regex" %}
          <p>Some text</p>
        {% endif %}
    """
    return re.match(regex, value)

