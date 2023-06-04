import functools
import re
import json

from flask import (
    Blueprint, flash, g, render_template, request, session
)


bp = Blueprint('create', __name__)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/create', methods=['POST'])
def create():
    body = request.form['body']
    names,data = create_data(body)

    return render_template('results.html', pokemons=names, weaknesses=data)



def create_data(body):

    final_data = {}

    # parse input and get names
    names = []
    mons = body.split("\r\n\r\n") #TODO is this gonna work on all platforms

    for mon in mons:
        mon_no_item_split = mon.split("\r\n")[0].split("@")[0].split(" ")
        for chunk in reversed(mon_no_item_split):
            if chunk not in ['(F)', '', '(M)']:
                names.append(chunk.strip("()"))
                break


    # read my file of weaknesses and get appropriate entries
    with open('data.json', encoding="utf-8") as f:
        data = json.load(f)

    result = []
    for name in names:
        result.append(data[name])


    pokemon_types = ["Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel"]

    for idx, pokemon_type in enumerate(pokemon_types):
        final_data[pokemon_type] = []
        for weaknesses in result:
            if weaknesses[idx] == 1 or weaknesses[idx] == 1.0:
                final_data[pokemon_type].append("")
            else:
                final_data[pokemon_type].append(weaknesses[idx])


    # calculate total weak and total resist
    for type in final_data:

        num_weak = 0
        num_resist = 0
        # append total weak
        for num in final_data[type]:
            if num == 2 or num == 4 or num == 2.0:
                num_weak += 1
            elif num == 0.5 or num == 0.25:
                num_resist += 1


        if num_weak == 0:
            final_data[type].append("")
        else:
            final_data[type].append(num_weak)
    
        if num_resist == 0:
            final_data[type].append("")
        else:
            final_data[type].append(num_resist)

    return names,final_data