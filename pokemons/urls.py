from django.conf.urls import url
from pokemons import views

urlpatterns = [
    url(r'^$', views.get_pokemons, name='get_pokemons'),
    url(r'^pokemons/(?P<pokemon_id>\d+)/$', views.get_pokemon, name='get_pokemon'),
]
