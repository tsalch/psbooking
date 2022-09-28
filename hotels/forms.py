from datetime import date

from django import forms
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe

from hotels.models import Country, Hotel, Reservation, Review, Room, Option
from utils.forms import update_fields_widget, update_fields_widget_dict, init_town


class HotelFilterFormDDC(forms.Form):
    COUNT_PERSON_CHOICE = ((1, 1), (2, 2), (3, 3), (4, 4), (5, 5))
    check_in = forms.DateField(label='Заезд',
                               widget=forms.DateInput(format="%Y-%m-%d", attrs={'type': 'date'}), required=True)
    check_out = forms.DateField(label='Отъезд',
                                widget=forms.DateInput(format="%Y-%m-%d", attrs={'type': 'date'}), required=True)
    person = forms.ChoiceField(label='Человек:', choices=COUNT_PERSON_CHOICE, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self, ('check_in', 'check_out',), 'form-control')
        self.fields['person'].widget.attrs.update({'class': 'form-group pr-4 m-0'})

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data['check_in']
        check_out = cleaned_data['check_out']
        if check_in < date.today():
            raise forms.ValidationError('Дата заезда не может быть меньше текущей')
        if check_out < check_in:
            raise forms.ValidationError('Дата отъезда должна быть не раньше!')
        return cleaned_data


class FindHotelFilterForm(forms.Form):
    choices = [(choice, mark_safe('<span class="bi bi-star-fill"></span>' * choice)) for choice in range(5, 0, -1)]
    person = forms.IntegerField(required=False)
    destination = forms.ModelChoiceField(queryset=Country.objects.all(), label='Направление', required=False)
    check_in = forms.DateField(label='Дата заезда',
                               widget=forms.DateInput(format="%Y-%m-%d", attrs={'type': 'date'}), required=False)
    check_out = forms.DateField(label='Дата отъезда',
                                widget=forms.DateInput(format="%Y-%m-%d", attrs={'type': 'date'}), required=False)
    available = forms.BooleanField(label='Только доступные варианты', required=False)
    price_min = forms.IntegerField(required=False)
    price_max = forms.IntegerField(required=False)
    stars = forms.MultipleChoiceField(choices=choices, required=False, widget=forms.CheckboxSelectMultiple)
    service = forms.ModelMultipleChoiceField(queryset=Option.objects.all(), required=False,
                                             widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self, ('person', 'check_in', 'check_out', 'price_min', 'price_max',), 'form-control')
        self.fields['person'].widget = forms.HiddenInput()
        self.fields['price_min'].widget.attrs.update({'placeholder': 'от'})
        self.fields['price_max'].widget.attrs.update({'placeholder': 'до'})
        self.fields['service'].widget.attrs.update({'class': 'form-check-input'})
        update_fields_widget(self, ('available', 'stars', 'service',), 'form-check-input')
        update_fields_widget_dict(self, ('price_min', 'price_max', 'stars', 'service',), {'form': 'idform'})

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data['check_in']
        check_out = cleaned_data['check_out']
        available = cleaned_data['available']
        person = cleaned_data['person']
        price_min = cleaned_data['price_min']
        price_max = cleaned_data['price_max']
        if price_min and price_max and price_min > price_max:
            price = price_max
            price_max = price_min
            price_min = price
            cleaned_data.update({'price_min': price_min, 'price_max': price_max})
        if check_in and check_in < date.today():
            raise forms.ValidationError('Дата заезда не может быть меньше текущей')
        if not available and not (check_in and check_out) and check_in != check_out:
            raise forms.ValidationError('Обе даты должны быть заполнены!')
        if available and not (check_in and check_out):
            raise forms.ValidationError('Обе даты должны быть заполнены!')
        if person and not (check_in and check_out):
            raise forms.ValidationError('Обе даты должны быть заполнены!')
        if check_in and check_out and check_in > check_out:
            raise forms.ValidationError('Дата отъезда должна быть не раньше!')
        return cleaned_data


class HotelReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ('user', 'hotel',):
            self.fields[field].widget = forms.HiddenInput()
        self.fields['rate'].widget.attrs.update({'class': 'form-control'})
        self.fields['text'].widget.attrs.update({'cols': '40', 'rows': 3, 'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()

        if 'user' not in cleaned_data:
            raise forms.ValidationError(f'Оставлять отзывы могут только зарегистрированные пользователи')

        if not Reservation.objects.filter(user=cleaned_data['user'], hotel=cleaned_data['hotel']).exists():
            raise forms.ValidationError('Вы не останавливались в этом отеле.')
        if Review.objects.filter(user=cleaned_data['user'], hotel=cleaned_data['hotel']).exists():
            raise forms.ValidationError('Вы уже оставили отзыв.')

        return cleaned_data

    def clean_rate(self):
        rate = self.cleaned_data['rate']
        if rate > 5:
            raise forms.ValidationError('Максимальная оценка - 5')
        return rate

    def get_redirect_url(self):
        hotel = self.cleaned_data.get('hotel', None)
        if not hotel:
            auto = get_object_or_404(Hotel, pk=self.data.get('hotel'))
        return hotel.get_absolute_url() if hotel else reverse_lazy('hotels:hotel_booking')


class HotelCreateForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ('picture', 'title', 'category', 'is_renovated', 'options', 'description', 'country', 'town',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self, ('picture', 'title', 'category', 'description'), 'form-control')
        self.fields['is_renovated'].widget.attrs.update({'class': 'form-check-label'})
        self.fields['options'].widget.attrs.update({'class': 'form-select'})
        init_town(self, kwargs)

    def clean_category(self):
        rate = self.cleaned_data['category']
        if rate > 5:
            raise forms.ValidationError('Максимальная звездность - 5')
        return rate

    def clean(self):
        cleaned_data = super().clean()
        quest = Hotel.objects.filter(title=self.cleaned_data.get('title', ''),
                                     country=self.cleaned_data.get('country', ''),
                                     town=self.cleaned_data.get('town', ''))
        id = self.instance.id
        msg = 'Такой отель уже есть'
        if not id:
            if quest.exists():
                raise forms.ValidationError(msg)
        else:
            found = quest.first()
            if found and found.id != id:
                raise forms.ValidationError(msg)
        if not (cleaned_data.get('country') and cleaned_data.get('town')):
            raise forms.ValidationError('Страна и город должны быть заполнены')
        return cleaned_data


class RoomCreateForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ('number', 'picture', 'room_class', 'price', 'capacity', 'description',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self, self.fields, 'form-control')
        self.fields['description'].widget.attrs.update({'cols': 40, 'rows': 3})


class BaseRoomCreateFormSet(forms.BaseInlineFormSet):
    def get_queryset(self):
        return Room.objects.none()

    def clean(self):
        """Проверим что добавляемые комнаты не имеют одинаковых номеров"""

        if any(self.errors):
            # если какая-либо из форм не прошла проверку, то ничего не выполняем
            return

        all_forms_is_empty = True
        numbers = []
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                # если форма помечена как удаленная, то пропускаем ее
                continue
            all_forms_is_empty = all_forms_is_empty and not any(form.cleaned_data)
            number = form.cleaned_data.get('number')
            if number and number in numbers:
                raise forms.ValidationError(f"В наборе присутствуют комнаты с одинаковым номером: {number}")
            numbers.append(number)

        if all_forms_is_empty:
            raise forms.ValidationError("Все формы пустые. Заполните данные.")


RoomFormSet = forms.inlineformset_factory(Hotel, Room, form=RoomCreateForm, formset=BaseRoomCreateFormSet, extra=2)
