from django import forms

from .models import Auction


class CreateAuctionForm(forms.ModelForm):
    deadline_date = forms.DateTimeField(
        label='Deadline date',
        help_text=
        'in format dd/mm/yyyy hh:mm:ss (for example: 30/12/2019 20:00:00”)',
        input_formats=['%d/%m/%Y %H:%M:%S'])

    class Meta:
        model = Auction
        fields = (
            "title",
            "description",
            "minimum_price",
            "deadline_date",
        )

        help_texts = {
            'minimum_price': 'Dot separated decimal value',
        }


class BidForm(forms.Form):
    bid = forms.DecimalField(
        label='Set bid amount',
        min_value=0,
        max_digits=10,
        decimal_places=2,
        help_text='Max two decimalplaces. Bids are in EUR')
