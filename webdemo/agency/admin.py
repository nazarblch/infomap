from django.contrib import admin
from agency.models import UserProfile
from agency.models import Clients
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


class ClientsAdmin(admin.ModelAdmin):
    list_display = ('login', 'name', 'agent')
admin.site.register(Clients, ClientsAdmin)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'


class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)