from django import template
from django.template import defaultfilters

from utils.text import plural_form
from allauth.socialaccount.models import SocialAccount

register = template.Library()


@register.simple_tag
def plural(value, form1, form2, form5):
    return plural_form(value, form1, form2, form5)


@register.filter(is_safe=True)
def label_with_classes(value, arg):
    return value.label_tag(attrs={'class': arg})


@register.simple_tag
def star_line(sc):
    return '<span class="bi bi-star-fill"></span>' * sc


@register.simple_tag
def is_available(obj, cin, cout):
    return obj.is_available(cin, cout)


@register.filter()
def get_val(dict, key):
    return dict.get(key, None)


@register.filter()
def num_dot(num):
    num = int(num)
    return f'{num:,}'.replace(',', '.')


@register.simple_tag()
def avatar(user):
    av = user.profile.avatar_url
    if av != '':
        return av
    else:
        sac = SocialAccount.objects
        if sac.filter(user=user).exists():
            av = sac.get(provider='vk', user=user).extra_data['photo_max_orig']
            return av
        else:
            return ''


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()
