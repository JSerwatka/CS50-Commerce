from django.contrib import admin
from .models import User, Auction, Bid, Comment, Watchlist

# Register your models here.

# User table - visible columns for admin view
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "password")

admin.site.register(User, UserAdmin)
admin.site.register(Auction)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Watchlist)