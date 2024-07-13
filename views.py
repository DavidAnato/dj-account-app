# Django imports
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives, send_mail
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.crypto import get_random_string
from django.utils import encoding
# Third-party imports
import requests
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
# Local imports
from .models import CustomUserModel
from .serializers import (
    UserRegistrationSerializer, OTPVerificationSerializer,
    EmailValidateRequestSerializer, LoginSerializer,
    GoogleLoginSerializer, ChangePasswordSerializer,
    SetPasswordSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)


User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    queryset = CustomUserModel.objects.all()
    serializer_class = UserRegistrationSerializer

    def perform_create(self, serializer):
        user = serializer.save()

        # Generate OTP
        otp_code = get_random_string(length=5, allowed_chars='1234567890')
        user.otp_code = otp_code
        user.otp_generated_at = timezone.now()
        user.save()

        # Generate activation link
        activation_link = self.request.build_absolute_uri(reverse('activate-account')) + f'?otp={otp_code}&email={user.email}'

        # Send email with OTP and activation link
        send_activation_email(user.email, otp_code, activation_link)

        return Response({'message': 'Activation email has been sent successfully.'}, status=status.HTTP_200_OK)

class EmailValidateRequestView(generics.CreateAPIView):
    serializer_class = EmailValidateRequestSerializer

    def perform_create(self, serializer):
        email = serializer.validated_data['email']

        try:
            user = CustomUserModel.objects.get(email=email, is_active=False)
        except CustomUserModel.DoesNotExist:
            return Response({"error": "User with this email not found or already activated."}, status=status.HTTP_404_NOT_FOUND)

        # Generate new OTP
        otp_code = get_random_string(length=5, allowed_chars='1234567890')
        user.otp_code = otp_code
        user.otp_generated_at = timezone.now()
        user.save()

        # Send email with new OTP
        activation_link = self.request.build_absolute_uri(reverse('activate-account')) + f'?otp={otp_code}&email={user.email}'
        send_activation_email(user.email, otp_code, activation_link)

        return Response({"message": "New OTP sent successfully."}, status=status.HTTP_200_OK)

class ActivateAccountView(generics.GenericAPIView):
    serializer_class = OTPVerificationSerializer

    def get(self, request, *args, **kwargs):
        otp_code = request.query_params.get('otp')
        email = request.query_params.get('email')

        if not otp_code or not email:
            return Response({"error": "OTP and email are required in query parameters."}, status=status.HTTP_400_BAD_REQUEST)

        return self.activate_account(email, otp_code)

    def post(self, request, *args, **kwargs):
        return self.activate_account(request.data.get('email'), request.data.get('otp'))

    def activate_account(self, email, otp_code):
        try:
            user = CustomUserModel.objects.get(email=email)
        except CustomUserModel.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_400_BAD_REQUEST)

        if user.otp_code != otp_code:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        if user.otp_generated_at and user.otp_generated_at + timezone.timedelta(hours=3) < timezone.now():
            return Response({"error": "OTP has expired. Please request a new OTP."}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.verified_email = True
        user.save()

        return Response({"message": "Your account has been activated successfully."}, status=status.HTTP_200_OK)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            "refresh": str(refresh),
            "access": access_token,
        }, status=status.HTTP_200_OK)

class GoogleLoginView(generics.GenericAPIView):
    serializer_class = GoogleLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']

        client_id = settings.GOOGLE_CLIENT_ID
        client_secret = settings.GOOGLE_CLIENT_SECRET
        redirect_uri = settings.GOOGLE_REDIRECT_URI

        # Exchange the authorization code for an access token
        token_response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': code,
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            }
        )
        token_json = token_response.json()
        access_token = token_json.get('access_token')

        if not access_token:
            return Response({"error": "Failed to obtain access token."}, status=status.HTTP_400_BAD_REQUEST)

        # Use the access token to obtain user info
        user_info_response = requests.get(
            'https://www.googleapis.com/oauth2/v1/userinfo',
            params={'access_token': access_token}
        )
        user_info = user_info_response.json()

        # Extract relevant user information
        email = user_info.get('email')
        first_name = user_info.get('given_name')
        last_name = user_info.get('family_name')
        google_id = user_info.get('id')
        picture_url = user_info.get('picture')
        verified_email = user_info.get('verified_email', False)

        if not email:
            return Response({"error": "Failed to obtain user email."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user already exists in the database
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'google_id': google_id,
                'picture_url': picture_url,
                'verified_email': verified_email,
                'is_active': True,
            }
        )

        if not created:
            # Update user information if necessary
            user.first_name = first_name
            user.last_name = last_name
            user.google_id = google_id
            user.picture_url = picture_url
            user.verified_email = verified_email
            user.save()

        # Generate JWT tokens for the user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            "refresh": str(refresh),
            "access": access_token,
        }, status=status.HTTP_200_OK)

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, queryset=None):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response({"detail": "Password updated successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SetPasswordView(generics.UpdateAPIView):
    serializer_class = SetPasswordSerializer
    model = User
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, queryset=None):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response({"detail": "Password set successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(generics.CreateAPIView):
    serializer_class = PasswordResetRequestSerializer

    def perform_create(self, serializer):
        email = serializer.validated_data['email']

        try:
            user = CustomUserModel.objects.get(email=email, is_active=True)
        except CustomUserModel.DoesNotExist:
            return Response({"error": "No active user found with this email."}, status=status.HTTP_404_NOT_FOUND)

        # Generate a password reset token and save it to the user
        token = default_token_generator.make_token(user)
        user.reset_password_token = token
        user.reset_password_token_created_at = timezone.now()
        user.save()

        # Send password reset email with token link
        reset_link = self.request.build_absolute_uri(reverse('password-reset-confirm', kwargs={'uidb64': urlsafe_base64_encode(force_bytes(user.pk)), 'token': token}))
        send_password_reset_email(user.email, reset_link)

        return Response({"message": "Password reset email has been sent successfully."}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(generics.UpdateAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uidb64 = kwargs['uidb64']
        token = kwargs['token']

        try:
            uid = encoding.force_text(urlsafe_base64_decode(uidb64))
            user = CustomUserModel.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUserModel.DoesNotExist):
            return Response({"error": "Invalid user id or token."}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            # Reset password
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid token. Please request a new password reset."}, status=status.HTTP_400_BAD_REQUEST)




def send_password_reset_email(email, reset_link):
    subject = 'Password Reset Request'
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Password Reset Request</title>
        <style>
            body {{
                background-color: #f3f4f6;
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                marging: 0 auto;
            }}
            .container {{
                max-width: 600px;
                padding: 20px;
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
            }}
            .btn {{
                display: inline-block;
                padding: 10px 20px;
                background-color: #007bff;
                color: #fff;
                text-decoration: none;
                border-radius: 3px;
                margin-top: 20px;
                font-size: 1.2rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">Password Reset Request</h2>
            <p>Hello,</p>
            <p>We received a request to reset your password. Click the button below to proceed:</p>
            <a href="{reset_link}" class="btn">Reset Password</a>
            <p style="margin-top: 20px;">If you did not request this, you can safely ignore this email.</p>
            <p>Regards,<br>The X-TECH Team</p>
        </div>
    </body>
    </html>
    """
    text_content = strip_tags(html_content)  # Strip the HTML tags to get the text version
    email = EmailMultiAlternatives(subject, text_content, from_email=settings.EMAIL_HOST_USER, to=[email])
    email.attach_alternative(html_content, "text/html")
    email.send()

def send_activation_email(email, otp_code, activation_link):
    subject = 'Activate Your Account'
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Activate Your Account</title>
        <style>
            body {{
                background-color: #f3f4f6;
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }}
            .container {{
                max-width: 600px;
                padding: 20px;
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
                marging: 0 auto;
            }}
            .btn {{
                display: inline-block;
                padding: 10px 20px;
                background-color: #007bff;
                color: #fff;
                text-decoration: none;
                border-radius: 3px;
                margin-top: 20px;
                font-size: 1.2rem;

            }}
            .otp-code {{
                font-size: 2rem;
                font-weight: 600;
                margin-top: 1.3rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">Activate Your Account</h2>
            <p>Hello,</p>
            <p>Thank you for registering with X-TECH. Your OTP for account activation is:</p>
            <p class="otp-code">{otp_code}</p>
            <hr style="margin: 20px 0;">
            or
            <hr style="margin: 20px 0;">
            <a href="{activation_link}" class="btn">Activate Account</a>
            <p style="margin-top: 20px;">This OTP is valid for 3 hours.</p>
            <p>Regards,<br>The X-TECH Team</p>
        </div>
    </body>
    </html>
    """
    text_content = strip_tags(html_content)  # Strip the HTML tags to get the text version
    email = EmailMultiAlternatives(subject, text_content, from_email=settings.EMAIL_HOST_USER, to=[email])
    email.attach_alternative(html_content, "text/html")
    email.send()
