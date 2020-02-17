from rest_framework import authentication, permissions, status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Auction
from .serializers import AuctionSerializer
from .views import make_bid


class BrowseAuctionApi(APIView):
    #permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def get(self, request, format=None):
        auctions = Auction.objects.filter(state=0)

        serializer = AuctionSerializer(auctions, many=True)
        return Response(serializer.data)


class SearchAuctionApi(APIView):
    #permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def get(self, request, *args, **kwargs):
        term = kwargs['pk']
        if term:
            auctions = Auction.objects.filter(title__icontains=term).filter(
                state=0)

        serializer = AuctionSerializer(auctions, many=True)
        return Response(serializer.data)


class SearchAuctionWithTermApi(APIView):
    def get(self, request):
        term = request.GET.get('term')
        auctions = Auction.objects.filter(title__icontains=term).filter(
            state=0)

        serializer = AuctionSerializer(auctions, many=True)
        return Response(serializer.data)


class SearchAuctionApiById(APIView):
    def get(self, request, *args, **kwargs):
        pk = kwargs['pk']
        auctions = Auction.objects.filter(id=pk).filter(state=0)
        serializer = AuctionSerializer(auctions, many=True)
        return Response(serializer.data)


class BidAuctionApi(APIView):
    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    parser_classes = [JSONParser]

    def post(self, request, pk, format=None):
        auction = Auction.objects.get(id=pk)
        bidder = request.user

        bid_amount = request.data.get("new_price")

        message = make_bid(auction, bidder, bid_amount)
        if message == 'success':
            #TODO description of the bid as json
            return Response(
                {
                    "message": "Bid successfully",
                    "title": auction.title,
                    "description": auction.description,
                    "current_price": bid_amount,
                    "deadline_date": auction.deadline_date
                },
                status=status.HTTP_200_OK)

        #TODO response as json
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    pass
