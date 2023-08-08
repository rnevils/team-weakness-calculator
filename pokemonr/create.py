import json
from flask import Blueprint, flash, g, render_template, request, session

bp = Blueprint("create", __name__)

with open("data.json", encoding="utf-8") as f:
    WEAKNESS_DATA = json.load(f)

POKEMON_TYPES = [
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


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/results", methods=["POST"])
def create():
    body = request.form["body"]

    try:
        names = parse_input(body)
        data = create_data(names)

        return render_template(
            "results.html",
            pokemons=names,
            weaknesses=data,
            get_class_matchup=get_class_matchup,
            get_class_resist_total=get_class_resist_total,
            get_class_weak_total=get_class_weak_total,
        )
    except KeyError as ke:
        return render_template("error.html"), 400


def get_class_matchup(matchup):
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


def get_class_weak_total(total_weak):
    if total_weak < 4:
        return f"total-weak-{total_weak}"
    else:
        return "total-weak-verybad"


def get_class_resist_total(total_resist):
    if total_resist < 4:
        return f"total-resist-{total_resist}"
    else:
        return "total-resist-verygood"


def parse_input(body):
    mons = body.split("\r\n\r\n")  # TODO is this gonna work on all platforms

    # extract names
    names = []
    for mon in mons:
        mon_no_item_split = mon.split("\r\n")[0].split("@")[0].split(" ")
        for chunk in reversed(mon_no_item_split):
            if chunk not in ["(F)", "", "(M)"]:
                names.append(chunk.strip("()"))
                break

    return names


def create_data(names):
    weaknesses_by_pokemon = [WEAKNESS_DATA[name] for name in names]
    final_data = {}

    # create weakness data for each type
    for idx, pokemon_type in enumerate(POKEMON_TYPES):
        matchups = [weaknesses[idx] for weaknesses in weaknesses_by_pokemon]
        weakness_data = {"matchups": matchups, "Total_Weak": 0, "Total_Resist": 0}
        final_data[pokemon_type] = weakness_data

    # calculate total weak and total resist
    for type in final_data:
        num_weak = num_resist = 0
        for num in final_data[type]["matchups"]:
            if num in [2, 4]:
                num_weak += 1
            elif num in [0.5, 0.25, 0]:
                num_resist += 1

        final_data[type]["Total_Weak"] = num_weak
        final_data[type]["Total_Resist"] = num_resist

    return final_data
