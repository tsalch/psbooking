from datetime import date

from allauth.account.views import LoginView, SignupView
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count, Subquery
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView, ListView, TemplateView

from accounts.forms import (CustomUserCreationForm, ProfileUpdateForm, UserUpdateForm,
                            CustomAuthenticationForm, CustomPasswordResetForm, CustomSetPasswordForm)
from accounts.models import Profile
from hotels.models import Reservation, Review, Hotel
from utils.views import book_rev


class NullUser:
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('main:index'))
        return super().get(request, *args, **kwargs)


class CustomSignUpView(SignupView):
    model = User
    template_name = 'accounts/registration/sign_up.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('main:index')


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/registration/sign_in.html'


class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'accounts/registration/password_reset_form.html'
    form_class = CustomPasswordResetForm
    email_template_name = 'accounts/registration/password_reset_email.txt'
    subject_template_name = 'accounts/registration/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')
    html_email_template_name = 'accounts/registration/password_reset_email.html'

    def form_valid(self, form):
        self.request.session['reset_email'] = form.cleaned_data['email']
        return super().form_valid(form)


class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'accounts/registration/password_reset_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reset_email'] = self.request.session.get('reset_email', '')
        context['reset_hostname'] = self.request.get_host()
        return context


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/registration/password_reset_confirm.html'
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('accounts:password_reset_complete')


class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'accounts/registration/password_reset_complete.html'


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')
    child_model = Profile
    child_form_class = ProfileUpdateForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_child_model(self):
        return self.child_model

    def get_child_fields(self):
        return self.child_fields

    def get_child_form(self, sv=False):
        kwargs = self.get_form_kwargs()
        if hasattr(self, 'object'): kwargs['instance'] = kwargs['instance'].profile
        return self.child_form_class(**kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'child_form' not in context:
            context['child_form'] = self.get_child_form()
        # user = self.request.user
        context['dashboard'] = True
        context['mprof'] = True
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        child_form = self.get_child_form(True)
        form.instance = self.request.user
        child_form.instance = self.request.user.profile

        # check if both forms are valid
        form_valid = form.is_valid()
        child_form_valid = child_form.is_valid()

        if form_valid and child_form_valid:
            return self.form_valid(form, child_form)
        else:
            return self.form_invalid(form, child_form)

    def form_valid(self, form, child_form):
        self.object = form.save()
        save_child_form = child_form.save(commit=False)
        save_child_form.course_key = self.object
        save_child_form.save()
        messages.success(self.request, f'Данные успешно обновлены')
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, child_form):
        messages.error(self.request, form.errors)
        return HttpResponseRedirect('.')


class BookingListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'accounts/booking_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dashboard'] = True
        context['mbook'] = True
        context['cancel'] = True if self.request.user.profile.role == 'u' else False
        context['today'] = date.today()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        queryset, reviews = book_rev(queryset, Review, user)
        queryset = queryset.annotate(rate=Subquery(reviews.values('rate')))
        return queryset


class ReviewListView(LoginRequiredMixin, ListView):
    model = Review
    template_name = 'accounts/review_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['dashboard'] = True
        context['mrev'] = True
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        queryset, rsvs = book_rev(queryset, Reservation, user)
        queryset = queryset.annotate(check_in=Subquery(rsvs.values('check_in')),
                                     check_out=Subquery(rsvs.values('check_out')))
        return queryset


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        role = self.request.user.profile.role
        context['dashboard'] = True
        context['mdash'] = True
        if role == Profile.USER_ROLE_USER:
            return context
        if role == Profile.USER_ROLE_ADMINISTRATOR:
            user_count = User.objects.count()
            user_count = user_count or 0
            res_count = Reservation.objects.count()
            res_count = res_count or 0
            rev_count = Review.objects.count()
            rev_count = rev_count or 0
            context.update({'user_count': user_count, 'res_count': res_count,
                            'rev_count': rev_count, 'visual': True})
        context['access'] = True
        hotels = Hotel.objects.annotate(res_count=Count('reservations', distinct=True))
        hotels = hotels.annotate(rev_count=Count('reviews', distinct=True)).all()
        hotels = hotels.select_related('town', 'country')
        context['hotels'] = hotels
        return context
