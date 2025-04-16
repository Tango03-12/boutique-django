from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Récupère la valeur d'un dictionnaire par sa clé"""
    return dictionary.get(key, None)


register = template.Library()

@register.filter
def mul(value, arg):
    try:
        return float(value) * int(arg)
    except (ValueError, TypeError):
        return 0
