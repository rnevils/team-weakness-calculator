import json
from flask import Blueprint, flash, g, render_template, request, session

from pokemonr.parse import parse_input

bp = Blueprint("create", __name__)

with open("data.json", encoding="utf-8") as f:
    WEAKNESS_DATA = json.load(f)

with open("moves.json", encoding="utf-8") as f:
    MOVES_DATA = json.load(f)

with open("weakness_types.json", encoding="utf-8") as f:
    WEAKNESS_TYPES = json.load(f)


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
        pokemon_team_parsed = parse_input(body)

        # your team
        names = [pokemon.name for pokemon in pokemon_team_parsed]

        # defensive coverage stats
        devensive_coverage_data = create_devensive_coverage_data(names)

        # pokemon you have no supereffective moves against
        all_moves = [pokemon.moves for pokemon in pokemon_team_parsed]
        pokemon_no_supereffective_against = get_pokemon_no_weakness(all_moves)

        return render_template(
            "results.html",
            names=names,
            weaknesses=devensive_coverage_data,
            pokemon_no_supereffective_against=pokemon_no_supereffective_against,
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


def create_devensive_coverage_data(names):
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


def get_pokemon_no_weakness(all_moves):
    # unpack list of lists, and create set of moves
    moves = {move for moves in all_moves for move in moves}

    # have to deal with hidden powers
    hidden_powers = {
        s[s.find("[") + 1 : s.find("]")].lower() for s in moves if "[" in s and "]" in s
    }

    # Remove the Hidden Power entries from the set
    moves = {
        s for s in moves if not (s.startswith("Hidden Power [") and s.endswith("]"))
    }

    # reach into database of moves and get info on the ones we have
    # have to
    moves_info = [MOVES_DATA[move.lower().replace(" ", "-")] for move in moves]

    # get which ones actually do damage (and not fixed damage)
    offensive_types = {move["type"] for move in moves_info if move["power"]}

    # add in the hidden power types
    offensive_types = offensive_types | hidden_powers

    # from those types, check entire pokedex to make sure which combos the set doesn't have anything supereffective against.
    result = {
        pokemon
        for pokemon, weak_types in WEAKNESS_TYPES.items()
        if not offensive_types.intersection(weak_types)
    }

    # filter that to relevant results... top 100 from gen 3 out smogon stats
    with open("top_100.txt") as file:
        top_100_mons = {line.rstrip() for line in file}

    return result.intersection(top_100_mons)
