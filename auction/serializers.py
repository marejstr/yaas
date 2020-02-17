from rest_framework import serializers

from .models import Auction


#TODO show creator name, not id
class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ('id', 'seller', 'title', 'description', 'minimum_price',
                  'deadline_date')
