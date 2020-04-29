from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin

from users.forms import CustomUserCreationForm, CustomUserChangeForm, RoleForm
from users.models import CustomUser, Role


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('nick', 'email', 'is_staff', 'is_active',)
    list_filter = ('joined', 'email', 'is_staff', 'is_active', 'role')
    fieldsets = (
        (None, {'fields': ('email', 'nick', 'password', 'role')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)


class RoleAdmin(admin.ModelAdmin):
    form = RoleForm


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Role, RoleAdmin)
