from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    fieldsets = UserAdmin.fieldsets + (
        ('Ustawienia Klonu Discorda', {
            'fields': ('role', 'avatar', 'description', 'is_blocked')
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)