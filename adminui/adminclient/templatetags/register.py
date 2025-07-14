from django.template.defaulttags import register

@register.filter
def get_dict_item(target_dict, key):
    return target_dict.get(key, '')