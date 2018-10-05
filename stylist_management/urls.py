from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^user-autocomplete/$', views.UserAutocomplete.as_view(), name='user-autocomplete',),
    url(r'^create_new_stylist/$', views.create_new_stylist, name='create_new_stylist',),
    url(r'^off_board_stylist/$', views.off_board_stylist, name='off_board_stylist',),
]