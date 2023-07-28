import functools
import re
import json

from flask import Blueprint, flash, g, render_template, request, session


bp = Blueprint("create", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/results", methods=["POST"])
def create():
    body = request.form["body"]
    names, data = create_data(body)

    return render_template(
        "results.html", pokemons=names, weaknesses=data, get_class=get_class
    )


def get_class(matchup):
    match matchup:
        case 0:
            return "no-effect"
        case 0.5:
            return "not-very-effective"
        case 0.25:
            return "very-not-very-effective"
        case 2:
            return "super-effective"
        case 4:
            return "very-super-effective"
        case _:
            return "normal-effective"

    return "matchup-20"


def create_data(body):
    names = []
    mons = body.split("\r\n\r\n")  # TODO is this gonna work on all platforms

    for mon in mons:
        mon_no_item_split = mon.split("\r\n")[0].split("@")[0].split(" ")
        for chunk in reversed(mon_no_item_split):
            if chunk not in ["(F)", "", "(M)"]:
                names.append(chunk.strip("()"))
                break

    with open("data.json", encoding="utf-8") as f:
        data = json.load(f)

    result = []
    for name in names:
        result.append(data[name])

    pokemon_types = [
        "Normal",
        "Fire",
        "Water",
        "Electric",
        "Grass",
        "Ice",
        "Fighting",
        "Poison",
        "Ground",
        "Flying",
        "Psychic",
        "Bug",
        "Rock",
        "Ghost",
        "Dragon",
        "Dark",
        "Steel",
    ]

    final_data = {}
    for idx, pokemon_type in enumerate(pokemon_types):
        matchups = []
        weakness_data = {}
        for weaknesses in result:
            if weaknesses[idx] == 1 or weaknesses[idx] == 1.0:
                matchups.append("")
            else:
                matchups.append(weaknesses[idx])
        weakness_data["matchups"] = matchups
        weakness_data["Total_Weak"] = ""
        weakness_data["Total_Resist"] = ""
        final_data[pokemon_type] = weakness_data

    for type in final_data:
        num_weak = 0
        num_resist = 0
        # append total weak
        for num in final_data[type]["matchups"]:
            if num in [2, 2.0, 4]:
                num_weak += 1
            elif num in [0.5, 0.25, 0]:
                num_resist += 1

        if num_weak == 0:
            final_data[type]["Total_Weak"] = ""
        else:
            final_data[type]["Total_Weak"] = num_weak

        if num_resist == 0:
            final_data[type]["Total_Resist"] = ""
        else:
            final_data[type]["Total_Resist"] = num_resist

    print(final_data)

    return names, final_data
