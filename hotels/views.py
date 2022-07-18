from datetime import datetime
from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.views.generic.edit import ProcessFormView

from hotels.models import Town, Hotel, Room, Review, Reservation
from utils.views import hotel_query
from .forms import FindHotelFilterForm, HotelReviewForm, HotelCreateForm, RoomCreateForm, RoomFormSet


class HotelListView(ListView):
    model = Hotel
    template_name = 'hotels/hotel_list.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_data = self.request.GET
        if get_data.get('check_in', False):
            self.request.session['check_in'] = get_data['check_in']
            self.request.session['check_out'] = get_data['check_out']
        else:
            if self.request.session.get('check_in', False): del self.request.session['check_in']
            if self.request.session.get('check_out', False): del self.request.session['check_out']
        context['filter_form'] = FindHotelFilterForm(get_data)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        form = FindHotelFilterForm(self.request.GET)
        if form.is_valid():
            filter_destination = form.cleaned_data['destination']
            filter_check_in = form.cleaned_data['check_in']
            filter_check_out = form.cleaned_data['check_out']
            filter_available = form.cleaned_data['available']
            filter_price_min = form.cleaned_data['price_min']
            filter_price_max = form.cleaned_data['price_max']
            filter_stars = form.cleaned_data['stars']
            filter_service = form.cleaned_data['service']
            filter_person = self.request.session.get('person', False)
            if filter_destination:
                queryset = queryset.filter(country=filter_destination)
            if filter_stars:
                queryset = queryset.filter(category__in=filter_stars)
            if filter_service:
                for service in filter_service:
                    queryset = queryset.filter(options__in=[service])
            if filter_price_min or filter_price_max:
                if filter_price_min:
                    hotels = [hotel.id for hotel in queryset if
                              hotel.rooms.filter(price__gte=filter_price_min).exists()]
                    queryset = queryset.filter(id__in=hotels)
                if filter_price_max:
                    hotels = [hotel.id for hotel in queryset if
                              hotel.rooms.filter(price__lte=filter_price_max).exists()]
                    queryset = queryset.filter(id__in=hotels)
            if filter_person:
                hotels = [hotel.id for hotel in queryset if
                          hotel.rooms.filter(capacity=filter_person).exists()]
                queryset = queryset.filter(id__in=hotels)
            if filter_check_in and filter_check_out and filter_available:
                hotels = [hotel.id for hotel in queryset if
                          hotel.is_available(filter_check_in, filter_check_out, filter_person)]
                queryset = queryset.filter(id__in=hotels)
        queryset = hotel_query(queryset)
        return queryset.order_by('-pk')


class HotelDetailView(DetailView):
    model = Hotel
    template_name = 'hotels/hotel_booking.html'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        default_object = super().get_object(queryset)
        return default_object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ses_data = self.request.session
        cin = ses_data.get('check_in', '--')
        cout = ses_data.get('check_out', '--')
        person = ses_data.get('person', False)
        if person:
            rooms = self.object.rooms.filter(capacity=person)
        else:
            rooms = self.object.rooms.all()
        if cin == '--':
            availability = 'Выберите даты'
        else:
            cin = datetime.strptime(cin, '%Y-%m-%d')
            cout = datetime.strptime(cout, '%Y-%m-%d')
            availability = 'Есть места' if self.object.is_available(cin, cout, person) else 'Мест нет'
            state = {}
            for room in rooms:
                state[room.id] = room.is_available(cin, cout)
            context['state'] = state
        context.update({'cin': cin, 'cout': cout, 'availability': availability})
        context['rooms'] = rooms
        reviews = self.object.reviews.select_related('user__profile').all()
        context['reviews'] = reviews
        context['avg_rate'] = self.object.favg_rate
        context['review_form'] = HotelReviewForm(initial={'user': self.request.user, 'hotel': self.object})
        context['person'] = True if person else False
        return context

    def get_template_names(self):
        default_template_names = super().get_template_names()
        return default_template_names


class HotelSendReview(LoginRequiredMixin, CreateView):
    model = Review
    form_class = HotelReviewForm

    def get_success_url(self):
        return self.object.hotel.get_absolute_url()

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return HttpResponseRedirect(form.get_redirect_url())


class HotelCreateView(LoginRequiredMixin, CreateView):
    model = Hotel
    form_class = HotelCreateForm
    template_name = 'hotels/hotel_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dashboard'] = True
        return context

    def get_success_url(self):
        return self.object.get_url_update()

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, 'Отель успешно создан')
        return super().form_valid(form)


class HotelUpdateView(LoginRequiredMixin, UpdateView):
    model = Hotel
    form_class = HotelCreateForm
    template_name = 'hotels/hotel_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dashboard'] = True
        context['edit'] = True
        context['rooms'] = self.object.rooms.all()
        return context

    def get_success_url(self):
        return self.object.get_url_update()

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, 'Данные успешно изменены.')
        return super().form_valid(form)


class RoomCreateView(LoginRequiredMixin, ProcessFormView, TemplateView):
    template_name = 'hotels/room_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hotel = get_object_or_404(Hotel, pk=self.kwargs.get('hotel_pk', ''))
        if self.request.method == 'POST':
            formset = RoomFormSet(self.request.POST, self.request.FILES, instance=hotel)
        else:
            formset = RoomFormSet(instance=hotel)
        context['formset'] = formset
        context['dashboard'] = True
        context['hotel'] = hotel
        return context

    def post(self, request, *args, **kwargs):
        hotel = get_object_or_404(Hotel, pk=kwargs.get('hotel_pk', ''))
        formset = RoomFormSet(request.POST, request.FILES, instance=hotel)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(reverse('hotels:hotel_update', args=[str(hotel.pk)]))
        return super().get(request, *args, **kwargs)


class RoomUpdateView(LoginRequiredMixin, UpdateView):
    model = Room
    form_class = RoomCreateForm
    template_name = 'hotels/room_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dashboard'] = True
        context['hotel'] = self.object.hotel
        context['rc'] = Room.room_class_dict[self.object.room_class]
        return context

    def get_success_url(self):
        return reverse('hotels:hotel_update', args=[str(self.object.hotel.pk)])

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, 'Данные успешно изменены.')
        return super().form_valid(form)


def room_book(request, pk):
    user = request.user
    if user and user.is_authenticated and request.session.get('person', False):
        room = get_object_or_404(Room, pk=pk)
        ses_data = request.session
        cin = ses_data['check_in']
        cout = ses_data['check_out']
        if not Reservation.objects.filter(user=request.user, hotel=room.hotel, room=room, check_in=cin,
                                          check_out=cout).exists():
            Reservation.objects.create(user=request.user, hotel=room.hotel, room=room, check_in=cin, check_out=cout)
            messages.info(request, 'Ваше бронирование успешно завершено')
        else:
            messages.info(request, 'Уже забронировано')
        return HttpResponseRedirect(reverse_lazy('accounts:booking_list'))
    else:
        return HttpResponseRedirect(reverse_lazy('accounts:sign_in'))


class ReservationDeleteView(LoginRequiredMixin, DeleteView):
    model = Reservation
    template_name = 'hotels/reservation_delete.html'
    success_url = reverse_lazy('accounts:booking_list')

    def get_object(self, queryset=None):
        reserv = super().get_object(queryset)
        if not Reservation.objects.filter(pk=reserv.pk).exists():
            messages.info(self.request, 'Брони уже нет')
            raise self.success_url
        else:
            return reserv

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dashboard'] = True
        return context

    def delete(self, request, *args, **kwargs):
        result = super().delete(request, *args, **kwargs)
        messages.success(request, f'Бронь {self.object} отменена.')
        return result


def load_towns(request):
    country_id = request.GET.get('country')
    if country_id:
        towns = Town.objects.filter(country_id=country_id).order_by('title')
    else:
        towns = Town.objects.none()
    return render(request, 'snippets/_town_dropdown_list.html', {'towns': towns})
