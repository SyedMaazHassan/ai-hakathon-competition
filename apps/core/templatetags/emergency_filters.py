from django import template

register = template.Library()

@register.filter
def filter_status(queryset, status):
    return [call for call in queryset if call.status == status]

@register.filter
def filter_priority(queryset, priority):
    return [call for call in queryset if call.priority == priority]