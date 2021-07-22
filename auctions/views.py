"""Contains implementation of all views used in this app"""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django import forms
# Error exceptions
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from .models import User, Auction, Bid, Comment, Watchlist

# ----------------------------------------------------------------------
# ------------------------------  Forms  -------------------------------
# ----------------------------------------------------------------------
class CreateListingForm(forms.ModelForm):
    """Creates form for Auction model."""
    title = forms.CharField(label="Title", max_length=20, required=True, widget=forms.TextInput(attrs={
                                                                            "autocomplete": "off",
                                                                            "aria-label": "title",
                                                                            "class": "form-control"
                                                                        }))
    description = forms.CharField(label="Description", widget=forms.Textarea(attrs={
                                    'placeholder': "Tell more about the product",
                                    'aria-label': "description",
                                    "class": "form-control"
                                    }))
    image_url = forms.URLField(label="Image URL", required=True, widget=forms.URLInput(attrs={
                                        "class": "form-control"
                                    }))

    category = forms.ChoiceField(required=True, choices=Auction.CATEGORY, widget=forms.Select(attrs={
                                        "class": "form-control"
                                    }))

    class Meta:
        model = Auction
        fields = ["title", "description", "category", "image_url"]

class BidForm(forms.ModelForm):
    """Creates form for Bid model."""
    class Meta:
        model = Bid
        fields = ["bid_price"]
        labels = {
            "bid_price": _("")
        }
        widgets = {
            "bid_price": forms.NumberInput(attrs={
                "placeholder": "Bid",
                "min": 0.01,
                "max": 100000000000,
                "class": "form-control"
            })
        }

class CommentForm(forms.ModelForm):
    """Creates form for Comment model."""
    class Meta:
        model = Comment
        fields = ["comment"]
        labels = {
            "comment": _("")
        }
        widgets = {
            "comment": forms.Textarea(attrs={
                "placeholder": "Comment here",
                "class": "form-control",
                "rows": 1
            })
        }

# ----------------------------------------------------------------------
# ------------------------------  Views  -------------------------------
# ----------------------------------------------------------------------
def index(request):
    """Main view: shows all listings."""
    # Get all auctions descending
    auctions = Auction.objects.filter(closed=False).order_by("-publication_date")

    return render(request, "auctions/index.html", {
        "auctions": auctions
    })

@login_required(login_url="auctions:login")
def user_panel(request):
    """User Panel view: shows all auctions that user:
        * is currently selling
        * sold
        * is currently bidding
        * won
    """
    # Helpers
    all_distinct_bids =  Bid.objects.filter(user=request.user.id).values_list("auction", flat=True).distinct()
    won = []

    # Get auctions currently being sold by the user
    selling = Auction.objects.filter(closed=False, seller=request.user.id).order_by("-publication_date").all()

    # Get auction sold by the user
    sold = Auction.objects.filter(closed=True, seller=request.user.id).order_by("-publication_date").all()

    # Get auctions currently being bid by the user
    bidding = Auction.objects.filter(closed=False, id__in = all_distinct_bids).all()

    # Get auctions won by the user
    for auction in Auction.objects.filter(closed=True, id__in = all_distinct_bids).all():
        highest_bid = Bid.objects.filter(auction=auction.id).order_by('-bid_price').first()

        if highest_bid.user.id == request.user.id:
            won.append(auction)

    return render(request, "auctions/user_panel.html", {
        "selling": selling,
        "sold": sold,
        "bidding": bidding,
        "won": won
    })

@login_required(login_url="auctions:login")
def create_listing(request):
    """Create Listing view: allows to add new listing through a form."""
    if request.method == "POST":
        form = CreateListingForm(request.POST)
        if form.is_valid():
            # Get all data from the form
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            category = form.cleaned_data["category"]
            image_url = form.cleaned_data["image_url"]

            # Save a record
            auction = Auction(
                seller = User.objects.get(pk=request.user.id),
                title = title,
                description = description,
                category = category,
                image_url = image_url
            )
            auction.save()
        else:
            return render(request, "auctions/create_listing.html", {
                "form": form
            })

    return render(request, "auctions/create_listing.html", {
        "form": CreateListingForm(),
    })

def listing_page(request, auction_id):
    """Listing Page view: shows detailed page of a single auction."""
    # Get current auction if exists
    try:
        auction = Auction.objects.get(pk=auction_id)
    except Auction.DoesNotExist:
        return render(request, "auctions/error_handling.html", {
            "code": 404,
            "message": "Auction id doesn't exist"
        })

    # Get info about bids
    bid_amount = Bid.objects.filter(auction=auction_id).count()
    highest_bid = Bid.objects.filter(auction=auction_id).order_by('-bid_price').first()

    # Show auction only to the winner and the seller if closed
    if auction.closed:
        if highest_bid is not None:
            winner = highest_bid.user

            # Diffrent view for winner, seller and other users
            if request.user.id == auction.seller.id:
                return render(request, "auctions/sold.html", {
                    "auction": auction,
                    "winner": winner
                })
            elif request.user.id == winner.id:
                return render(request, "auctions/bought.html", {
                    "auction": auction
                })
        else:
            if request.user.id == auction.seller.id:
                return render(request, "auctions/closed_no_offer.html", {
                    "auction": auction
                })

        return HttpResponse("Error - auction no longer available")
    else:
         # If user logged in, check if auction already in watchlist
        if request.user.is_authenticated:
            watchlist_item = Watchlist.objects.filter(
                    auction = auction_id,
                    user = User.objects.get(id=request.user.id)
            ).first()

            if watchlist_item is not None:
                on_watchlist = True
            else:
                on_watchlist = False
        else:
            on_watchlist = False

        # Get all the comments
        comments = Comment.objects.filter(auction=auction_id)

        # Check who has made the highest bid
        if highest_bid is not None:
            if highest_bid.user == request.user.id:
                bid_message = "Your bid is the highest bid"
            else:
                bid_message = "Highest bid made by " + highest_bid.user.username
        else:
            bid_message = None

        return render(request, "auctions/listing_page.html", {
            "auction": auction,
            "bid_amount": bid_amount,
            "bid_message": bid_message,
            "on_watchlist": on_watchlist,
            "comments": comments,
            "bid_form": BidForm(),
            "comment_form": CommentForm()
        })

@login_required(login_url="auctions:login")
def watchlist(request):
    """Watchlist views: shows all auctions that are on user's watchlist."""
    # Save info about the auction and go back to auction's page
    if request.method == "POST":
        # Info about the auction
        auction_id = request.POST.get("auction_id")

        # Make sure that auction exists
        try:
            auction = Auction.objects.get(pk=auction_id)
            user = User.objects.get(id=request.user.id)
        except Auction.DoesNotExist:
            return render(request, "auctions/error_handling.html", {
                "code": 404,
                "message": "Auction id doesn't exist"
            })

        # Add/delete from watchlist logic
        if request.POST.get("on_watchlist") == "True":
            # Delete it from watchlist model
            watchlist_item_to_delete = Watchlist.objects.filter(
                user = user,
                auction = auction
            )
            watchlist_item_to_delete.delete()
        else:
            # Save it to watchlist model
            try:
                watchlist_item = Watchlist(
                    user = user,
                    auction = auction
                )
                watchlist_item.save()
            # Make sure it is not duplicated for current user
            except IntegrityError:
                return render(request, "auctions/error_handling.html", {
                    "code": 400,
                    "message": "Auction is already on your watchlist"
                })

        return HttpResponseRedirect("/" + auction_id)


    watchlist_auctions_ids = User.objects.get(id=request.user.id).watchlist.values_list("auction")
    watchlist_items = Auction.objects.filter(id__in=watchlist_auctions_ids, closed=False)

    return render(request, "auctions/watchlist.html", {
        "watchlist_items": watchlist_items
    })

@login_required(login_url="auctions:login")
def bid(request):
    """Bid view: only POST method allowed, handles bidding logic."""
    if request.method == "POST":
        form = BidForm(request.POST)
        if form.is_valid():
            bid_price = float(form.cleaned_data["bid_price"])
            auction_id = request.POST.get("auction_id")

            # Make sure that bid_price is positive
            if bid_price <= 0:
                return render(request, "auctions/error_handling.html", {
                    "code": 400,
                    "message": "Bid price must be greater than 0"
                })

            # # Make sure that auction exists
            try:
                auction = Auction.objects.get(pk=auction_id)
                user = User.objects.get(id=request.user.id)
            except Auction.DoesNotExist:
                return render(request, "auctions/error_handling.html", {
                    "code": 404,
                    "message": "Auction id doesn't exist"
                })

            # Make sure that bid is not made by the seller
            if auction.seller == user:
                return render(request, "auctions/error_handling.html", {
                    "code": 400,
                    "message": "Seller cannot bid"
                })

            # Check if current bid is the highest / else save new bid
            highest_bid = Bid.objects.filter(auction=auction).order_by('-bid_price').first()
            if highest_bid is None or bid_price > highest_bid.bid_price:
                # Add new bid to db
                new_bid = Bid(auction=auction, user=user, bid_price=bid_price)
                new_bid.save()

                # Update current highest price
                auction.current_price = bid_price
                auction.save()

                return HttpResponseRedirect("/" + auction_id)
            else:
                return render(request, "auctions/error_handling.html", {
                    "code": 400,
                    "message": "Youre bid is too small"
                })
        else:
            return render(request, "auctions/error_handling.html", {
                "code": 400,
                "message": "Form is invalid"
            })
    # Method not allowed - GET
    return render(request, "auctions/error_handling.html", {
        "code": 405,
        "message": "Method Not Allowed"
    })

def categories(request, category=None):
    """Categories view: shows all categories and allowes filter auction by category."""
    # Get all possible categories
    categories_list = Auction.CATEGORY

    # Check if valid category as URL parameter
    if category is not None:
        if category in [x[0] for x in categories_list]:
            category_full = [x[1] for x in categories_list if x[0] == category][0]

            # Get all auctions from this category
            auctions = Auction.objects.filter(category=category, closed=False)
            return render(request, "auctions/category.html", {
                "auctions": auctions,
                "category_full": category_full
            })
        else:
            return render(request, "auctions/error_handling.html", {
                "code": 400,
                "message": "Category is incorrect"
            })

    return render(request, "auctions/error_handling.html", {
        "code": 404,
        "message": "This page doesn not exist"
    })


@login_required(login_url="auctions:login")
def close_auction(request, auction_id):
    """Close Auction view: only POST method allowed, handles closing auction logic."""
    # Get current auction if exists
    try:
        auction = Auction.objects.get(pk=auction_id)
    except Auction.DoesNotExist:
        return render(request, "auctions/error_handling.html", {
            "code": 404,
            "message": "Auction id doesn't exist"
        })

    # Close auction
    if request.method == "POST":
        auction.closed = True
        auction.save()
    elif request.method == "GET":
        return render(request, "auctions/error_handling.html", {
            "code": 405,
            "message": "Method Not Allowed"
        })

    # Redirect to auction page
    return HttpResponseRedirect("/" + auction_id)

@login_required(login_url="auctions:login")
def handle_comment(request, auction_id):
    """Handle comment view: only POST method allowed, handles posting comments on auction."""
    # Get current auction if exists
    try:
        auction = Auction.objects.get(pk=auction_id)
    except Auction.DoesNotExist:
        return render(request, "auctions/error_handling.html", {
            "code": 404,
            "message": "Auction id doesn't exist"
        })

    # Post comment
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            # Get all data from the form
            comment = form.cleaned_data["comment"]

            # Save a record
            comment = Comment(
                user=User.objects.get(pk=request.user.id),
                comment = comment,
                auction = auction
            )
            comment.save()
        else:
            return render(request, "auctions/error_handling.html", {
                "code": 400,
                "message": "Form is invalid"
            })
    elif request.method == "GET":
        return render(request, "auctions/error_handling.html", {
            "code": 405,
            "message": "Method Not Allowed"
        })

    # Redirect to auction page
    return HttpResponseRedirect("/" + auction_id)

def login_view(request):
    """Login view: handles log in logic."""
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)

            # If user tried to enter login_required page - go there after login
            if "next" in request.POST:
                return HttpResponseRedirect(reverse("auctions:" + request.POST.get("next")[1:]))
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    """Logout view: handles logout logic."""
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    """Register view: handles register logic."""
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")

def handle_not_found(request, exception):
    return render(request, "auctions/error_handling.html", {
            "code": 404,
            "message": "Page not found"
        })