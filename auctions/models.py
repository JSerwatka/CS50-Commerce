from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Auction(models.Model):
    # Categories - choices
    MOTORS = "MOT"
    FASHINON = "FAS"
    ELECTRONICS = "ELE"
    COLLECTIBLES_ARTS = "ART"
    HOME_GARDES = "HGA"
    SPORTING_GOODS = "SPO"
    TOYS = "TOY"
    BUSSINES_INDUSTRIAL = "BUS"
    MUSIC = "MUS"

    CATEGORY = [
        (MOTORS, "Motors"),
        (FASHINON, "Fashion"),
        (ELECTRONICS, "Electronics"),
        (COLLECTIBLES_ARTS, "Collectibles & Art"),
        (HOME_GARDES, "Home & Garden"),
        (SPORTING_GOODS, "Sporting Goods"),
        (TOYS, "Toys"),
        (BUSSINES_INDUSTRIAL, "Business & Industrial"),
        (MUSIC, "Music"),
    ]

    # Model fields
    # auto: auction_id
    seller_id = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=64, blank=False)
    description = models.TextField(blank=True)
    current_price = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    category = models.CharField(max_length=3, choices=CATEGORY, default=MOTORS)
    image_url = models.URLField(blank=True)
    publication_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "auction"
        verbose_name_plural = "auctions"

class Bid(models.Model):
    # Model fields
    # auto: bid_id
    auction_id = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_date = models.DateTimeField(auto_now_add=True)
    bid_price = models.DecimalField(max_digits=11, decimal_places=2)

    class Meta:
        verbose_name = "bid"
        verbose_name_plural = "bids"

class Comment(models.Model):
    # Model fields
    # auto: comment_id
    auction_id = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(blank=False)

    class Meta:
        verbose_name = "comment"
        verbose_name_plural = "comments"


class Watchlist(models.Model):
    # Model field
    # auto: watchlist_id
    auction_id = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "watchlist"
        verbose_name_plural = "watchlists"

