from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
# Error exceptions
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from .models import User, Auction, Bid, Comment, Watchlist

# ----------------------
# ------  Forms  -------
# ----------------------

class CreateListingForm(forms.ModelForm):
    title = forms.CharField(label="Title", max_length=64, required=True, widget=forms.TextInput(attrs={
                                                                            "autocomplete": "off",
                                                                            "aria-label": "title"
                                                                        }))
    description = forms.CharField(label="Description", widget=forms.Textarea(attrs={      
                                    'placeholder': "Tell more about the product",
                                    'aria-label': "description"
                                    }))
    image_url = forms.URLField(label="Image URL", required=False)

    class Meta:
        model = Auction
        fields = ["title", "description", "category", "image_url"]

# ----------------------
# ------  Views  -------
# ----------------------
def index(request):
    # Get all auctions descending
    auctions = Auction.objects.all().order_by("-publication_date")

    return render(request, "auctions/index.html", {
        "auctions": auctions
    })

@login_required(login_url="auctions:login")
def create_listing(request):
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
                seller_id=User.objects.get(id=request.user.id),
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
    # Get current auction
    auction = Auction.objects.get(pk=auction_id)

    # Get info about bids
    bid_amount = Bid.objects.filter(auction_id=auction_id).count()
    highest_bid = Bid.objects.order_by('-bid_price').first()

    # Check who has made the highest bid
    if highest_bid is not None:
        if highest_bid.user_id == request.user.id:
            bid_message = "Your bid is the current bid"
        else:
            bid_message = "Highest bid made by " + highest_bid.user_id.username
    else:
        bid_message = None

    return render(request, "auctions/listing_page.html", {
        "auction": auction,
        "bid_amount": bid_amount,
        "bid_message": bid_message
    })

@login_required(login_url="auctions:login")
def watchlist(request):
    # Save info about the auction and go back to auction's page
    if request.method == "POST":
        # Info from listing page
        auction_id = request.POST.get("auction_id")
        previous_page = request.POST.get('next')

        # Make sure, that id of page and id of auction are the same
        if auction_id != previous_page[1:]:
            #TODO: update error page
            return HttpResponse("Error-please don't change my html code")
        
        # Save it to watchlist model
        try:
            watchlist_item = Watchlist(
                auction_id = Auction.objects.get(pk=auction_id),
                user_id = User.objects.get(id=request.user.id)
            )
            watchlist_item.save()
        # Make sure that auction exists
        except Auction.DoesNotExist:
            #TODO: update error page
            return HttpResponse("Error-auction id doesn't exist")
        # Make sure that it is not duplicate for current user
        except IntegrityError:
            #TODO: update error page
            return HttpResponse("Error-auction already in your watchlist")

        return HttpResponseRedirect(previous_page)

    watchlisted = Watchlist.objects.filter(user_id=request.user.id)

    return render(request, "auctions/watchlist.html", {
        "watchlisted": watchlisted
    })


def login_view(request):
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
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
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
