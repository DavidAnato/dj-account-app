from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUserModel

@admin.register(CustomUserModel)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['date_joined', 'last_login']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'google_id', 'picture_url', 'picture', 'verified_email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login',)}),
        ('OPT', {'fields':('otp_code', 'otp_generated_at')})
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )

    ordering = ['-date_joined']

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-date_joined')

