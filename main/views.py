from datetime import datetime

from django.contrib import messages
from django.db.models import Min
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from hotels.forms import HotelFilterFormDDC
from hotels.models import Country, Hotel, Review

from allauth.socialaccount.models import SocialAccount

from utils.views import hotel_query

from django.db.models import F

class IndexView(TemplateView):
    template_name = 'main/index.html'

    def get(self, request, *args, **kwargs):
        form = HotelFilterFormDDC(request.GET)
        if request.GET.get('search', '') == '1':
            if form.is_valid():
                cd = form.cleaned_data
                check_in = cd['check_in']
                check_out = cd['check_out']
                person = cd['person']
                param = ''
                if check_in:
                    param = f'?check_in={check_in}'
                    self.request.session['check_in'] = datetime.strftime(check_in, '%Y-%m-%d')
                if check_out:
                    sn = '?' if len(param) == 0 else '&'
                    param += f'{sn}check_out={check_out}'
                    self.request.session['check_out'] = datetime.strftime(check_out, '%Y-%m-%d')
                if person:
                    sn = '?' if len(param) == 0 else '&'
                    param += f'{sn}person={person}'
                    self.request.session['person'] = person
                return HttpResponseRedirect(f"{reverse_lazy('hotels:hotel_list')}{param}")
            else:
                messages.error(request, form.non_field_errors())
        else:
            get_data = self.request.session
            if get_data.get('check_in', False): del get_data['check_in']
            if get_data.get('check_out', False): del get_data['check_out']
            if get_data.get('person', False): del get_data['person']
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['country_list'] = Country.objects.annotate(
            min_price=Min('hotels__rooms__price')).all().order_by('-id')[:3]
        context['hotel_list'] = hotel_query(Hotel.objects).order_by('-avg_rate')[:3]
        context['review_list'] = Review.objects.select_related('hotel', 'user__profile').all().order_by('-id')[:3]
        context['filter_form'] = HotelFilterFormDDC()
        return context
