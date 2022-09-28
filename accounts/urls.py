from django.contrib.auth.views import LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.urls import path, reverse_lazy

from . import views
from .forms import CustomPasswordChangeForm

app_name = 'accounts'

urlpatterns = [
    path('sign-up/', views.CustomSignUpView.as_view(), name='sign_up'),
    path('sign-in/', views.CustomLoginView.as_view(), name='sign_in'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('password-change/',
         PasswordChangeView.as_view(
             template_name='accounts/registration/change_password.html',
             form_class=CustomPasswordChangeForm,
             success_url=reverse_lazy('accounts:password_change_done'),
             extra_context={'dashboard': True}
         ),
         name='change_password'),
    path('password-change-done/',
         PasswordChangeDoneView.as_view(
             template_name='accounts/registration/change_password_done.html',
             extra_context={'dashboard': True}
         ),
         name='password_change_done'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset-done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password/reset/<str:uidb64>/<str:token>', views.CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password-reset-complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('booking-list/', views.BookingListView.as_view(), name='booking_list'),
    path('review-list/', views.ReviewListView.as_view(), name='review_list'),
]
