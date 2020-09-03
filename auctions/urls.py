"""Contains urls for all app's views"""
from django.urls import path

from . import views

app_name = "auctions"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("user_panel", views.user_panel, name="user_panel"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("<int:auction_id>", views.listing_page, name="listing_page"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("bid", views.bid, name="bid"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.categories, name="categories"),
    path("close_auction/<str:auction_id>", views.close_auction, name="close_auction"),
    path("handle_comment/<str:auction_id>", views.handle_comment, name="handle_comment")
]
