from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Fields to display in the admin list view
    list_display = ('email', 'first_name', 'last_name', 'phone', 'is_staff', 'is_active',)
    list_filter = ('is_staff', 'is_superuser', 'is_active',)
    # list_select_related = ('city',)

    # Fields to be used in the add and change forms
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'profile_picture')}),
        ('Location', {'fields': ('area',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Fields used when creating a new user via the admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone', 'city', 'area', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active'),
        }),
    )

    # Fields for search functionality
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('email',)

# Register the custom user model with the admin
admin.site.register(CustomUser, CustomUserAdmin)
