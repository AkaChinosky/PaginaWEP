from django import template
import json

register = template.Library()

@register.filter(name='json_loads')
def json_loads(value):
    return json.loads(value)


from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    return value * arg
