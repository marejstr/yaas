from django.urls import path, re_path

from . import views

app_name = 'auction'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('search/', views.Search.as_view(), name='search'),
    path('banned/', views.BannedView.as_view(), name='banned'),
    path('create/', views.CreateAuction.as_view(), name='create'),
    path('confirm/', views.ConfirmAuction.as_view(), name='confirm'),
    re_path(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
    re_path(r'^edit/(?P<pk>\d+)/$', views.EditAuction.as_view(), name='edit'),
    re_path(r'^edit/(?P<pk>\d+)/(?P<token>.+)/$',
            views.EditAuctionWithToken.as_view(),
            name='editwithtoken'),
    re_path(r'^bid/(?P<pk>\d+)/$', views.Bid.as_view(), name='bid'),
    re_path(r'^ban/(?P<pk>\d+)$', views.Ban.as_view(), name='ban'),
    path('resolve/', views.resolve, name='resolve')
]
