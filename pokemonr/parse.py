from typing import NamedTuple
import re

POKEMON_WITH_UNKNOWN_GENDER = set(
    [
        "Magnemite",
        "Magneton",
        "Voltorb",
        "Electrode",
        "Ditto",
        "Staryu",
        "Starmie",
        "Porygon",
        "Porygon2",
        "Shedinja",
        "Lunatone",
        "Solrock",
        "Baltoy",
        "Claydol",
        "Beldum",
        "Metang",
        "Metagross",
        "Articuno",
        "Zapdos",
        "Moltres",
        "Mewtwo" "Mew",
        "Lugia",
        "Ho-Oh",
        "Celebi",
        "Unown",
        "Raikou",
        "Entei",
        "Suicune",
        "Regirock",
        "Regice",
        "Registeel",
        "Latias",
        "Latios",
        "Kyogre",
        "Groudon",
        "Rayquaza",
        "Jirachi",
        "Deoxys",
        "Deoxys-Defense",
        "Deoxys-Speed",
        "Deoxys-Attack",
    ]
)

DEFAULT_IVS = {"HP": 31, "Atk": 31, "Def": 31, "SpA": 31, "SpD": 31, "Spe": 31}
DEFAULT_EVS = {"HP": 0, "Atk": 0, "Def": 0, "SpA": 0, "SpD": 0, "Spe": 0}


class Pokemon(NamedTuple):
    name: str
    item: str = None
    gender: str = "Random"
    ability: str = None
    level: int = 100
    shiny: bool = False
    happiness: int = None
    nature: str = None
    evs: dict = None
    ivs: dict = None
    moves: list = None


def extract_field(field_name, text, pattern=None):
    if not pattern:
        pattern = f"{field_name}: ([^\n]+)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else None


def process_values(values_string, iv=False):
    if iv:
        values = {"HP": 31, "Atk": 31, "Def": 31, "SpA": 31, "SpD": 31, "Spe": 31}
    else:
        values = {"HP": 0, "Atk": 0, "Def": 0, "SpA": 0, "SpD": 0, "Spe": 0}
    value_matches = re.findall(r"(\d+) (\w+)", values_string)
    for value, stat in value_matches:
        values[stat] = int(value)
    return values


def process_first_line(first_line):
    name = None
    gender = None
    item = None

    first_line_reversed = " ".join(reversed(first_line.split()))

    # split on first @
    first_line_reversed_split = first_line_reversed.split("@")

    # get item
    if len(first_line_reversed_split) > 1:
        # super edge case where pokmeon has no item and nickname contains "@"
        if first_line_reversed_split[0][0] == "(":
            name = first_line_reversed_split[0].split(")")[0].strip("(")
        else:
            item = " ".join(reversed(first_line_reversed_split[0].strip().split()))

        # 2nd element will have optional gender and then name
        for chunk in first_line_reversed_split[1].strip().split():
            if chunk == "(F)":
                gender = "Female"
            elif chunk == "(M)":
                gender = "Male"
            if chunk not in ["(F)", "", "(M)"]:
                name = chunk.strip("()")
                break
    else:
        name = first_line_reversed_split[0].split(" ")[0].strip("() ")

    if not gender:
        gender = "Unknown" if name in POKEMON_WITH_UNKNOWN_GENDER else "Random"

    return name, gender, item


def parse_section(section):
    first_line = section.split("\r\n")[0]
    name, gender, item = process_first_line(first_line)

    ability = extract_field("Ability", section)
    level_value = extract_field("Level", section)
    level = int(level_value) if level_value else 100
    shiny = True if extract_field("Shiny", section) == "Yes" else False
    happiness_value = extract_field("Happiness", section)
    happiness = int(happiness_value) if happiness_value else 255
    nature = extract_field("Nature", section, pattern=r"(\w+) Nature")
    evs_string = extract_field("EVs", section)
    ivs_string = extract_field("IVs", section)
    moves = [move.strip() for move in re.findall(r"- ([^\n]+)", section)]
    evs = process_values(evs_string) if evs_string else DEFAULT_EVS.copy()
    ivs = process_values(ivs_string, iv=True) if ivs_string else DEFAULT_IVS.copy()

    # Create a Pokemon instance
    return Pokemon(
        name=name,
        item=item,
        gender=gender,
        ability=ability,
        level=level,
        shiny=shiny,
        happiness=happiness,
        nature=nature,
        evs=evs,
        ivs=ivs,
        moves=moves,
    )


def parse_input(input):
    # Split the string into separate sections for each Pokemon
    pokemon_sections = input.strip().split("\r\n\r\n")
    pokemons = [parse_section(section) for section in pokemon_sections]
    return pokemons
