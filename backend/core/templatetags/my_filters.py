
from django import template

register = template.Library()

@register.filter
def get_items_for_event(items_dict, event_id):
    items = []
    for wishlist in items_dict.values():
        for item in wishlist:
            # Обращаемся к полю list_id через поле fields
            if item['fields']['list_id'] == event_id:
                items.append(item)
                print('!!!!!!!!!!!!!!!!!!!!!!!1')
                print(item['fields']['title'])  # Выводим название элемента
    return items


@register.filter
def filter_by_event_id(lists, event_id):
    for i in lists:
        if i.event_id == event_id:
            return i
    return None