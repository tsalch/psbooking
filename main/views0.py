from django.shortcuts import render
from django.db.models import Avg, Min, Count
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from hotels.forms import HotelFilterFormDDC
from hotels.models import Country, Hotel, Review
from utils.views import hotel_query


class IndexView(TemplateView):
    template_name = 'main/index.html'

    def get(self, request, *args, **kwargs):
        check_in = request.GET.get('check_in', '')
        check_out = request.GET.get('check_out', '')
        person = request.GET.get('person', '')
        if request.GET.get('search', '') == '1':
            param = ''
            if check_in:
                param = f'?check_in={check_in}'
            if check_out:
                sn = '?' if len(param) == 0 else '&'
                param += f'{sn}check_out={check_out}'
            if person:
                sn = '?' if len(param) == 0 else '&'
                param += f'{sn}person={person}'
            return HttpResponseRedirect(f"{reverse_lazy('hotels:hotel_list')}{param}")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['country_list'] = Country.objects.annotate(
            min_price=Min('hotels__rooms__price')).all().order_by('id')[:3]
        context['hotel_list'] = hotel_query(Hotel.objects)[:3]
        context['review_list'] = Review.objects.all().order_by('id')[:3]
        context['filter_form'] = HotelFilterFormDDC()
        return context
