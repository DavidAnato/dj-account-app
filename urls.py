from django.urls import path
from .views import ChangePasswordView, EmailValidateRequestView, GoogleLoginView, LoginView, PasswordResetConfirmView, PasswordResetRequestView, SetPasswordView, UserRegistrationView, ActivateAccountView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('activate/', ActivateAccountView.as_view(), name='activate-account'),
    path('validate/', EmailValidateRequestView.as_view(), name='email-validate'),
    path('login/', LoginView.as_view(), name='login'),
    path('google-login/', GoogleLoginView.as_view(), name='google-login'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('set-password/', SetPasswordView.as_view(), name='set-password'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]
