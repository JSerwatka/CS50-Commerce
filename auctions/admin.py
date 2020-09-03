"""Contains configuration on how to show all models in admin page."""

from django.contrib import admin
from .models import User, Auction, Bid, Comment, Watchlist

# Register your models here.

# User table - visible columns for admin view
class UserAdmin(admin.ModelAdmin):
    """Contains User model admin page config"""
    list_display = ("id", "username", "email", "password")

class AuctionAdmin(admin.ModelAdmin):
    """Contains Auction model admin page config"""
    list_display = ("id", "title", "category", "current_price",
                    "publication_date", "closed", "seller")

class BidAdmin(admin.ModelAdmin):
    """Contains Bid model admin page config"""
    list_display = ("auction", "user", "bid_price", "bid_date")

class CommentAdmin(admin.ModelAdmin):
    """Contains Comment model admin page config"""
    list_display = ("auction", "user", "comment")

class WatchlistAdmin(admin.ModelAdmin):
    """Contains Watchlist model admin page config"""
    list_display = ("auction", "user")

admin.site.register(User, UserAdmin)
admin.site.register(Auction, AuctionAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Watchlist, WatchlistAdmin)
