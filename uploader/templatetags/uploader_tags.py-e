from django import template
register = template.Library()

@register.simple_tag
def add_attr(field, **kwargs):
    return field.as_widget(attrs=kwargs)
