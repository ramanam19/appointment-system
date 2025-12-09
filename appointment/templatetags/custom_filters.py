from django import template

register = template.Library()

@register.filter
def time(value, arg):
    """
    Custom filter to format time
    """
    if value:
        return value.strftime(arg)
    return ''