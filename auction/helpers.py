import random
from datetime import datetime, timedelta
from decimal import *
from uuid import uuid4

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from auction.models import Auction, Bid


def generateData():
    Bid.objects.all().delete()
    Auction.objects.all().delete()
    User.objects.all().delete()

    u = User(username='admin')
    u.set_password('admin')
    u.is_superuser = True
    u.is_staff = True
    u.save()

    for i in range(50):
        a = Auction(title="Auction" + str(i),
                    seller=generateUser(i),
                    description="Same description as every auction",
                    minimum_price=random.randint(100, 2000) / 100,
                    deadline_date=generateDeadlineDate(),
                    token=str(uuid4()))
        a.save()

    for i in range(50):
        auc = Auction.objects.order_by('?').first()
        usr = User.objects.order_by('?').first()
        if auc.seller is not usr:
            bid = Bid(auction=auc, bidder=usr, bid_amount=generatebid(auc))
            bid.save()


def generateUser(i):
    return User.objects.create_user(username='User' + str(i),
                                    email='user' + str(i) + '@yaas.com',
                                    password='user' + str(i))


def generateDeadlineDate():
    delta = timedelta(days=random.randint(4, 20),
                      seconds=random.randint(5, 55),
                      minutes=random.randint(5, 55),
                      hours=random.randint(1, 20))
    deadline = timezone.now() + delta

    return deadline.strftime("%Y-%m-%d %H:%M:%S")


def generatebid(auc):

    highest_bid = None

    try:
        highest_bid = auc.bid_set.latest('bid_amount')
    except ObjectDoesNotExist:
        pass

    if highest_bid:
        bid = highest_bid.bid_amount + Decimal(random.randint(1, 5))
    else:
        bid = auc.minimum_price + Decimal(random.randint(1, 5))

    return bid
