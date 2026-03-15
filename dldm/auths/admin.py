from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
<<<<<<< HEAD
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
=======
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'role')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('Role', {'fields': ('role',)}),
>>>>>>> b87c717 (all project)
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
<<<<<<< HEAD
            'fields': ('username', 'email', 'password1', 'password2'),
=======
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'phone_number'),
>>>>>>> b87c717 (all project)
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
