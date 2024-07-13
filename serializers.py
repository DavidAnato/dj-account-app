from rest_framework import serializers
from .models import CustomUserModel
from django.contrib.auth import authenticate

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUserModel
        fields = ['email', 'first_name', 'last_name', 'password']

class OTPVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=5)
    email = serializers.EmailField()
    
    def validate_otp(self, value):
        try:
            user = CustomUserModel.objects.get(otp_code=value, is_active=False, verified_email=False)
            return user
        except CustomUserModel.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP. Please try again.")

class EmailValidateRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid email or password.")
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'.")

        data['user'] = user
        return data

class GoogleLoginSerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate_code(self, value):
        if not value:
            raise serializers.ValidationError("Authorization code is required.")
        return value

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value

    def validate_new_password(self, value):
        # Add any additional password validations here
        return value

class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        # Add any additional password validations here
        return value
    
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=6, write_only=True)
