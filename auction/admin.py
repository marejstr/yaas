from django.contrib import admin

from auction.models import Auction, Bid, UserCurrency, UserLanguage

admin.site.register(Auction)
admin.site.register(Bid)
admin.site.register(UserLanguage)
admin.site.register(UserCurrency)
