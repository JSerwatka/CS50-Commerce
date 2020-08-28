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
    # fk: user_Id #TODO
    category = models.CharField(max_length=3, choices=CATEGORY, default=MOTORS)
    publication_date = models.DateTimeField(auto_now_add=True)

class Bid(models.Model):
    # Model fields
    # auto: bid_id
    # fk: auction_id #TODO
    # fk: user_id #TODO
    bid_date = models.DateTimeField(auto_now_add=True)
    bid_price = models.DecimalField(max_digits=11, decimal_places=2)

class Comment(models.Model):
    # Model fields
    # auto: comment_id
    # fk: auction_id #TODO
    # fk: user_id #TODO
    comment = models.TextField()

class Watchlis(models.Model):
    # Model field
    # auto: watchlist_id
    # fk: auction_id #TODO
    # fk: user_id #TODO
    pass
