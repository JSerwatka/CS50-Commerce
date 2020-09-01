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


#TODO: delete next page in watchlist and use just auction id
#TODO: the same in bid
#TODO: delete next page in watchlist and use just auction id
#TODO: the same in bid
#TODO: change all _id in models to without _id
#TODO: adimn page update
#TODO: comment section create
#TODO: user page - sold and bought

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

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ["bid_price"]
        labels = {
            "bid_price": _("")
        }
        widgets = {
            "bid_price": forms.NumberInput(attrs={
                "placeholder": "Bid"
            })
        }
# ----------------------
# ------  Views  -------
# ----------------------
def index(request):
    # Get all auctions descending
    auctions = Auction.objects.filter(closed=False).order_by("-publication_date")

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
    # Get current auction if exists
    try:
        auction = Auction.objects.get(pk=auction_id)
    except Auction.DoesNotExist:
        #TODO: update error page
        return HttpResponse("Error-auction id doesn't exist")

    if request.method == "POST": 
        # Close auction
        auction.closed = True
        auction.save()

    # Get info about bids
    bid_amount = Bid.objects.filter(auction_id=auction_id).count()
    highest_bid = Bid.objects.filter(auction_id=auction_id).order_by('-bid_price').first()

    
    # Show auction only to the winner if no longer available
    if auction.closed:
        print(highest_bid)
        if highest_bid is not None:
            winner = highest_bid.user_id
            print(winner)
            print(auction.seller_id.id)
            print(request.user.id)
            # Diffrent view for winner, seller and other users
            if request.user.id == auction.seller_id.id:
                return render(request, "auctions/sold.html", {
                    "auction": auction,
                    "winner": winner
                })
            elif request.user.id == winner.id:
                return render(request, "auctions/bought.html", {
                    "auction": auction
                })
            else:
                return HttpResponse("Error - auction no longer available")

    else:
         # If user logged in, check if auction already in watchlist
        if request.user.is_authenticated:
            watchlist_item = Watchlist.objects.filter(
                    auction_id = auction_id,
                    user_id = User.objects.get(id=request.user.id)
            ).first()

            if watchlist_item is not None:
                on_watchlist = True
            else:
                on_watchlist = False
        else:
            on_watchlist = False

        # Check who has made the highest bid
        if highest_bid is not None:
            if highest_bid.user_id == request.user.id:
                bid_message = "Your bid is the highest bid"
            else:
                bid_message = "Highest bid made by " + highest_bid.user_id.username
        else:
            bid_message = None

        return render(request, "auctions/listing_page.html", {
            "auction": auction,
            "bid_amount": bid_amount,
            "bid_message": bid_message,
            "on_watchlist": on_watchlist,
            "bid_form": BidForm(),
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
        
        # Make sure that auction exists
        try:
            auction_id = Auction.objects.get(pk=auction_id)
            user_id = User.objects.get(id=request.user.id)
        except Auction.DoesNotExist:
            #TODO: update error page
            return HttpResponse("Error-auction id doesn't exist")

        if request.POST.get("on_watchlist") == "True":
            # Delete it from watchlist model
            watchlist_item_to_delete = Watchlist.objects.filter(
                user_id = user_id,
                auction_id = auction_id
            )
            watchlist_item_to_delete.delete()
        else:
            # Save it to watchlist model
            try:
                watchlist_item = Watchlist(
                    user_id = user_id,
                    auction_id = auction_id
                )
                watchlist_item.save()
            # Make sure it is not duplicated for current user
            except IntegrityError:
                #TODO: update error page
                return HttpResponse("Error-auction already in your watchlist")

        return HttpResponseRedirect(previous_page)


    watchlist_auctions_ids = User.objects.get(id=request.user.id).watchlist.values_list("auction_id")
    watchlist_items = Auction.objects.filter(id__in=watchlist_auctions_ids, closed=False)

    return render(request, "auctions/watchlist.html", {
        "watchlist_items": watchlist_items
    })

@login_required(login_url="auctions:login")
def bid(request):
    if request.method == "POST":
        form = BidForm(request.POST)
        if form.is_valid():
            bid_price = float(form.cleaned_data["bid_price"])
            # Info from listing page
            auction_id = request.POST.get("auction_id")
            previous_page = request.POST.get('next')
            
            # Make sure that bid_price is positive
            if bid_price <= 0:
                #TODO: update error page
                return HttpResponse("Error - bid price must be greate than 0")

            # # Make sure, that id of page and id of auction are the same
            if auction_id != previous_page[1:]:
                #TODO: update error page
                return HttpResponse("Error-please don't change my html code")
            
            # # Make sure that auction exists
            try:
                auction_id = Auction.objects.get(pk=auction_id)
                user_id = User.objects.get(id=request.user.id)
            except Auction.DoesNotExist:
                #TODO: update error page
                return HttpResponse("Error-auction id doesn't exist")

            # Make sure that bid is not made by the seller
            if auction_id.seller_id == user_id:
                #TODO: update error page
                return HttpResponse("Error- you are the seller")

            # Check if current bid is the highest / else save new bid
            highest_bid = Bid.objects.filter(auction_id=auction_id).order_by('-bid_price').first()
            if highest_bid is None or bid_price > highest_bid.bid_price:
                # Add new bid to db
                new_bid = Bid(auction_id=auction_id, user_id=user_id, bid_price=bid_price)
                new_bid.save()

                # Update current highest price
                auction_id.current_price = bid_price
                auction_id.save()

                return HttpResponseRedirect(previous_page)
            else:

                #TODO: update error page
                return HttpResponse("Error- Your bid is to small")
    #TODO: update error page
    return HttpResponse("Error - this method is not allowed")

def categories(request, category=None):
    # Get all possible categories
    categories = Auction.CATEGORY

    # Check if valid category as URL parameter
    if category is not None:
        if category in [x[0] for x in categories]:
            # Get all auctions from this category
            auctions = Auction.objects.filter(category=category, closed=False)
            return render(request, "auctions/category_auctions.html", {
                "auctions": auctions
            })
        else:
            #TODO: update error page
            return HttpResponse("Error - category incorrect")

    return render(request, "auctions/categories.html", {
        "categories": categories
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
