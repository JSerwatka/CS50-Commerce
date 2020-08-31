from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

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
    # Get all auctions
    auctions = Auction.objects.all()

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
    auction = Auction.objects.get(pk=auction_id)

    return render(request, "auctions/listing_page.html", {
        "auction": auction
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
