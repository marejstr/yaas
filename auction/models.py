from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Auction(models.Model):

    title = models.CharField(max_length=250)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    minimum_price = models.DecimalField(max_digits=10, decimal_places=2)
    deadline_date = models.DateTimeField()
    version = models.IntegerField(default=0)
    # state of the auction. 0 = active
    #                       1 = banned
    #                       2 = due
    #                       3 = resolved
    state = models.IntegerField(default=0)
    token = models.CharField(max_length=250)

    def __str__(self):
        return self.title


class UserCurrency(models.Model):

    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                primary_key=True)
    currency = models.CharField(max_length=3, default='EUR')

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserCurrency.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.usercurrency.save()


class UserLanguage(models.Model):

    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                primary_key=True)
    language = models.CharField(max_length=3, default='en')

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserLanguage.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.userlanguage.save()


class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
