from django.contrib import admin
from .models import User

# Register your models here.

# User table - visible columns for admin view
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "password")

admin.site.register(User, UserAdmin)