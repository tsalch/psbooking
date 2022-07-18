from hotels.models import Country, Town


def update_fields_widget(form, fields, css_class):
    for field in fields:
        form.fields[field].widget.attrs.update({'class': css_class})


def update_fields_widget_dict(form, fields, dict):
    for field in fields:
        form.fields[field].widget.attrs.update(dict)


def init_town(form, pars):
    inst = pars.get('instance')
    if inst:
        form.fields['town'].queryset = Town.objects.filter(country=inst.country).order_by('title')
    else:
        form.fields['town'].queryset = Town.objects.none()

    if 'country' in form.data:
        try:
            country_id = int(form.data.get('country'))
            form.fields['town'].queryset = Town.objects.filter(country_id=country_id).order_by('title')
        except (ValueError, TypeError):
            pass  # invalid input from the client; ignore and fallback to empty City queryset
    elif form.instance.country:
        form.fields['town'].queryset = form.instance.country.towns.all().order_by('title')
