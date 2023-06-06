import math

from django.http import Http404
from django.shortcuts import render
import requests
from django.urls import reverse

BASE_URL = 'https://pokeapi.co/api/v2'


def get_last_page(count, limit):
    calculated_number = math.floor(int(count) / int(limit))
    return int(calculated_number)


def get_page_dict(count, offset, limit):
    page_dict = []

    can_use_previous_page = offset - limit >= 0
    if can_use_previous_page:
        previous_page_number = int(offset / limit)
        previous_page = {
            "name": previous_page_number,
            "value": offset - limit
        }
        page_dict.append(previous_page)

    current_page_number = int(offset / limit) + 1
    current_page = {
        "name": current_page_number,
        "value": offset,
        "highlight": True
    }
    page_dict.append(current_page)

    can_use_next_page = (offset + limit) < count
    if can_use_next_page:
        next_page_number = int(offset / limit) + 2
        next_page_config = {
            'value': offset + limit,
            'name': next_page_number
        }
        page_dict.append(next_page_config)

    return page_dict


def get_pokemons_by_type(request, type):
    url = '{}/type/{}'.format(BASE_URL, type)
    response = requests.get(url)
    data = response.json()

    pokemons = []
    for pokemon in data['pokemon']:
        url = pokemon['pokemon']['url']
        response = requests.get(pokemon['pokemon']['url'])
        data_pokemon = response.json()
        pokemon_id = url.split('/')[-2]
        pokemon = {
            'name': data_pokemon.get('name'),
            'image': data_pokemon.get('sprites').get('front_default'),
            'id': int(pokemon_id)
        }
        pokemons.append(pokemon)

    context = {
        'count': len(pokemons),
        'type': data['name'],
        'pokemons': pokemons
    }
    return render(request, 'pokemons/pokemons_list.html', context)


# Create your views here.
def get_pokemons(request):
    type = request.GET.get('type', None)
    if type:
        type = int(type)
        return get_pokemons_by_type(request, type)
    offset = int(request.GET.get('offset', '0'))
    limit = int(request.GET.get('limit', '5'))
    params = {
        'offset': offset,
        'limit': limit,
        'type': type
    }

    url = BASE_URL + '/pokemon'
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Http404

    data = response.json()

    if not data.get('count'):
        raise Http404
    if not data.get('results'):
        raise Http404

    pokemons_list = data['results']
    pokemons_data = []

    for pokemon in pokemons_list:
        if not pokemon.get('url'):
            raise Http404
        url = pokemon.get('url')
        response = requests.get(url)

        if response.status_code != 200:
            raise Http404

        data_pokemon = response.json()
        pokemon_id = url.split('/')[-2]
        pokemon = {
            'name': data_pokemon.get('name'),
            'image': data_pokemon.get('sprites').get('front_default'),
            'id': int(pokemon_id)
        }
        pokemons_data.append(pokemon)

    pages_config = {
        "previous_page": {
            "name": 'Previous',
            "value": offset - limit,
            "disabled": (offset - limit) < 0,
        },
        "next_page": {
            "name": 'Next',
            "value": offset + limit,
            "disabled": (offset + limit) >= data['count'],
        },
        "last_page": {
            "name": get_last_page(data['count'], limit),
            "value": data['count'] - limit,
        },
        "pages": get_page_dict(count=data['count'], limit=limit, offset=offset)
    }

    context = {
        "count": data['count'],
        "pages_config": pages_config,
        "pokemons": pokemons_data
    }
    return render(request, 'pokemons/pokemons_list.html', context)


def get_pokemon(request, pokemon_id):
    url = '{}/pokemon/{}'.format(BASE_URL, pokemon_id)
    response = requests.get(url)

    if response.status_code != 200:
        raise Http404

    data = response.json()

    def add_pokemon_id(type):
        type_id = type['type']['url'].split('/')[-2]
        type = {
            'type': {
                'name': type['type']['name'],
                'id': type_id
            }
        }
        return type

    types = map(add_pokemon_id, data.get('types', []))

    context = {
        'pokemon': {
            'name': data.get('name'),
            'image': data.get('sprites').get('front_default'),
            'weight': data.get('weight'),
            'height': data.get('height'),
            'abilities': data.get('abilities'),
            'moves': data.get('moves'),
            'types': types
        }
    }
    return render(request, 'pokemons/pokemons_detail.html', context)
