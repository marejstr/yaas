import logging
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytz
import requests
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone, translation
from django.views import View, generic

from .forms import BidForm, CreateAuctionForm
from .helpers import generateData
from .models import Auction


class IndexView(generic.ListView):
    template_name = 'index.html'

    def get_queryset(self):
        return Auction.objects.filter(state=0)


class BannedView(UserPassesTestMixin, generic.ListView):
    # test if user is staff with the UserPassesTestMixin
    def test_func(self):
        return self.request.user.is_staff

    template_name = 'index.html'

    def get_queryset(self):
        return Auction.objects.filter(state=1)


class Search(generic.ListView):
    template_name = 'index.html'

    def get_queryset(self):
        query = self.request.GET.get('term')
        if query:
            return Auction.objects.filter(title__icontains=query).filter(
                state=0)
        else:
            return Auction.objects.filter(state=0)


class DetailView(View):
    form_class = BidForm
    template_name = 'detail.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        currency = request.session.get('currency', 'EUR')
        pk = kwargs['pk']
        auction = get_object_or_404(Auction, pk=pk)
        bids = auction.bid_set.all()

        if currency != 'EUR':
            exchange_rate = ExchangeRates.get_exchange_rate(currency)
            auction.minimum_price = Decimal(auction.minimum_price *
                                            exchange_rate).quantize(
                                                Decimal('0.01'))
            for bid in bids:
                bid.bid_amount = Decimal(
                    bid.bid_amount * exchange_rate).quantize(Decimal('0.01'))

        return render(request, self.template_name, {
            'form': form,
            'auction': auction,
            'bids': bids
        })


class CreateAuction(LoginRequiredMixin, View):
    def get(self, request):
        form = CreateAuctionForm()
        return render(request, "create_auction.html", {'form': form})

    def post(self, request):
        form = CreateAuctionForm(request.POST)
        if form.is_valid():

            date = request.POST.get('deadline_date', '')
            timezoneobj = datetime.strptime(date, '%d/%m/%Y %H:%M:%S')
            currenttime = timezone.get_current_timezone()
            timezoneobj = timezoneobj.replace(tzinfo=currenttime)

            if timezone.now() + timezone.timedelta(days=3) > timezoneobj:
                messages.error(
                    request, 'The deadline needs to be 72 hours in the future')
                return render(request, "create_auction.html", {'form': form})
            else:
                return render(request, "confirm_auction.html", {'form': form})
        else:
            return render(request, "create_auction.html", {'form': form})


class ConfirmAuction(LoginRequiredMixin, View):
    def post(self, request):

        form = CreateAuctionForm(request.POST)
        if form.is_valid():
            if 'cancel' in request.POST:
                return redirect("auction:index")

            token = str(uuid4())

            auction = form.save(commit=False)
            user = request.user
            auction.seller = user
            auction.token = token
            auction = form.save()

            auction_id = auction.id

            link1 = "http://127.0.0.1:8000/auction/" + str(auction_id)
            link2 = "http://127.0.0.1:8000/auction/edit/" + str(
                auction_id) + "/" + token

            send_mail(
                'Auction created on YAAS',
                'Hello, you have created a new auction on YAAS.\n link: ' +
                link1 + "\nEdit link: " + link2,
                'yaas@yaas.com',
                [user.email],
                fail_silently=False,
            )
            return redirect("auction:detail", pk=auction.pk)
        else:
            return render(request, "confirm_auction.html", {'form': form})


class EditAuction(LoginRequiredMixin, View):
    template_name = "edit_auction.html"

    def get(self, request, pk, *args, **kwargs):
        auction = get_object_or_404(Auction, pk=pk)

        if auction.seller.id is not request.user.id:
            messages.error(request, 'This is not your auction to edit')
            return redirect("auction:detail", pk=pk)
        elif auction.state != 0:
            messages.error(request, 'The auction is not active')
            return redirect("auction:detail", pk=pk)
        else:
            return render(request, self.template_name, {'auction': auction})

    def post(self, request, *args, **kwargs):
        description = request.POST.get('description', '')
        pk = kwargs['pk']
        auction = get_object_or_404(Auction, pk=pk)
        auction.description = description
        auction.version = auction.version + 1
        auction.save()
        messages.success(request, 'Auction has been updated successfully')
        return redirect("auction:detail", pk=pk)


class EditAuctionWithToken(View):
    template_name = "edit_auction.html"

    def get(self, request, pk, token, *args, **kwargs):
        auction = get_object_or_404(Auction, pk=pk)

        logger = logging.getLogger(__name__)
        logger.error(type(token))
        logger.error(token)
        logger.error(type(auction.token))
        logger.error(auction.token)

        if auction.token != token:
            messages.error(request, 'This is not your auction to edit')
            return redirect("auction:detail", pk=pk)
        elif auction.state != 0:
            messages.error(request, 'The auction is not active')
            return redirect("auction:detail", pk=pk)
        else:
            return render(request, self.template_name, {'auction': auction})

    def post(self, request, *args, **kwargs):
        description = request.POST.get('description', '')
        pk = kwargs['pk']
        auction = get_object_or_404(Auction, pk=pk)
        auction.description = description
        auction.version = auction.version + 1
        auction.save()
        messages.success(request, 'Auction has been updated successfully')
        return redirect("auction:detail", pk=pk)


class Bid(LoginRequiredMixin, View):
    form_class = BidForm
    template_name = 'detail.html'

    def post(self, request, pk):
        form = self.form_class(request.POST)
        auction = get_object_or_404(Auction, pk=pk)
        bids = auction.bid_set.all()
        message = ""
        if form.is_valid():
            bid_amount = form.cleaned_data['bid']
            edited_auction_version = request.POST['auction_version']
            if int(edited_auction_version) < auction.version:
                message = "The description was edited or  before bid, check it before you bid again"
            else:
                message = make_bid(auction, request.user, bid_amount)
                if message == "success":
                    messages.success(request, 'You has bid successfully')
                    return redirect("auction:detail", pk=pk)

        form.add_error('bid', message)

        return render(request, self.template_name, {
            'form': form,
            'auction': auction,
            'bids': bids
        })


class Ban(UserPassesTestMixin, View):
    # test if user is staff with the UserPassesTestMixin
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, *args, **kwargs):
        pk = kwargs['pk']
        auction = get_object_or_404(Auction, pk=pk)
        auction.state = 1
        auction.save()
        bids = auction.bid_set.all()
        send_mail(
            'Banned auction on YAAS',
            'Hello, your auction has been banned on YAAS',
            'yaas@yaas.com',
            [auction.seller.email],
            fail_silently=False,
        )
        for bid in bids:
            send_mail(
                'Auction banned on YAAS',
                'Hello, an auction you bid on has been banned on YAAS',
                'yaas@yaas.com',
                [bid.bidder.email],
                fail_silently=False,
            )
        messages.success(request, 'Ban successfully')
        return redirect("auction:detail", pk=pk)

    pass


def resolve(request):
    now = timezone.now()
    auctions = Auction.objects.filter(deadline_date__lt=now).filter(state=0)
    if auctions.exists():
        for auction in auctions:
            auction.state = 3
            auction.save()

            send_mail(
                'Auction fisnished on YAAS',
                'Hello, your auction finished on YAAS',
                'yaas@yaas.com',
                [auction.seller.email],
                fail_silently=False,
            )

            bids = auction.bid_set.all()
            if bids.exists():
                for bid in bids:
                    send_mail(
                        'Auction finished',
                        'Hello, an auction you bid on has finished on YAAS',
                        'yaas@yaas.com',
                        [bid.bidder.email],
                        fail_silently=False,
                    )
    return redirect("index")


def generate(request):
    generateData()
    return redirect("index")


def changeLanguage(request, lang_code):
    translation.activate(lang_code)
    request.session[translation.LANGUAGE_SESSION_KEY] = lang_code
    messages.success(request, 'language has beenchanged to ' + lang_code)

    if request.user.is_authenticated:
        user = request.user
        user.userlanguage.language = lang_code
        user.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def changeCurrency(request, currency_code):
    currency = request.session.get('currency', 'EUR')
    request.session['currency'] = currency_code
    request.session.modified = True
    messages.success(request, 'currency has beenchanged to ' + currency_code)

    if request.user.is_authenticated:
        user = request.user
        user.usercurrency.currency = currency_code
        user.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def make_bid(auction, bidder, bid_amount):
    decimal_bid_amount = Decimal(bid_amount).quantize(Decimal('0.01'))
    highest_bid = None
    try:
        highest_bid = auction.bid_set.latest('bid_amount')
    except ObjectDoesNotExist:
        pass

    if highest_bid and highest_bid.bid_amount >= decimal_bid_amount or auction.minimum_price > Decimal(
            bid_amount):
        message = 'New bid must be greater than the current bid for at least 0.01'
    elif bidder.id is auction.seller.id:
        message = "You cannot bid on your own auctions"
    elif auction.state == 1:
        message = "You can only bid on active auctions"
    elif auction.state == 3:
        message = "You can only bid on active auctions"
    elif auction.deadline_date < timezone.now():
        message = "You can only bid on active auctions"
    else:
        auction.bid_set.create(bidder=bidder, bid_amount=bid_amount)
        #send_mail(
        #    'Bid on YAAS',
        #    'Hello, you have just bid on a auction on YAAS',
        #    'yaas@yaas.com',
        #    [bidder.email],
        #    fail_silently=False,
        #)
        send_mail(
            'New bin on YAAS',
            'Hello, there is a new bin on your auction on YAAS',
            'yaas@yaas.com',
            [auction.seller.email],
            fail_silently=False,
        )
        if highest_bid:
            # only sending to the highest bidder not to spam all
            send_mail(
                'Overbidden on YAAS',
                'Hello you have bin overbidden on YAAS',
                'yaas@yaas.com',
                [highest_bid.bidder.email],
                fail_silently=False,
            )
        message = "success"
    return message


class ExchangeRates:
    json = None
    last_update = None

    @classmethod
    def get_exchange_rate(cls, currency):
        logger = logging.getLogger(__name__)
        logger.error("Update!")
        if cls.last_update is None or cls.last_update + timezone.timedelta(
                days=1) < timezone.now():
            r = requests.get('https://api.exchangeratesapi.io/latest?base=EUR')
            cls.json = r.json()
            cls.last_update = timezone.now()

        return Decimal(cls.json['rates'][currency])
