from dataclasses import asdict, fields
import os
from nicegui import ui
from Combat_Testing import Creature, Stats


def get_character_list():
    files = os.listdir("characters")
    characters = [f.replace(".json", "") for f in files if f.endswith(".json")]
    # characters = [f for f in files]

    return characters

def class_to_text(data):
    stats_dict = asdict(data)
    return ",\n".join(f"{k}:{v}" for k, v in stats_dict.items())

def get_widget_values(widget_dict):
    return {k: w.value for k, w in widget_dict.items()}

def selection_menu(title: str, options: list, filter_out=None):

    ui.label(title)
    selected_label = ui.label("None")

    state = {"value": None}

    def select(value):
        state["value"] = value
        selected_label.set_text(value)

    for option in options:
        if option != filter_out:
            ui.button(
                option,
                on_click=lambda o=option: select(o)
            )

    return state


def build_number_inputs(cls, filter=None): #FILTER ONLY BUILD INPUTS FROM ENTRIES WITH MATCHING METADATA TAG

    inputs = {}

    for f in fields(cls):

        if filter is not None:
            if not f.metadata.get(filter, False):
                continue

        widget = ui.number(f.name.capitalize(), value=1)

        inputs[f.name] = widget

    return inputs


# MAIN MENU
@ui.page('/')
def main_menu():
    ui.label('Main Menu').classes('text-h4')

    ui.button(
        'Characters',
        on_click=lambda: ui.navigate.to('/characters')
    )


# CHARACTER LIST
@ui.page('/characters')
def character_menu():
    ui.label('Characters').classes('text-h4')

    ui.button('Back', on_click=lambda: ui.navigate.to('/'))

    ui.button('Create', on_click=lambda: ui.navigate.to('/characters/create'))

    for name in get_character_list():
        # data = Creature.load(name)
        ui.button(
            name,
            on_click=lambda n=name: ui.navigate.to(f'/character/{n}')
        )


@ui.page('/characters/create')
def create_character():

    ui.label("Create Character").classes("text-h4")


    ui.button(
        'Back to Characters',
        on_click=lambda: ui.navigate.to('/characters')
    )

    #FUNCTION: input object, get field names, create a bunch of ui.numbers for each field name, stores them to a dictionary that should update with changing values, return the dictionary

    char_name = ui.input("Name", value="Player")
    char_stats = build_number_inputs(Stats, filter="base")

    status_label = ui.label("")

    def create_character():
        Creature(
            char_name.value,
            Stats(**get_widget_values(char_stats))
        )

        status_label.set_text(f"{char_name.value} created")

    ui.button(
        "Create",
        on_click=create_character
    )
    # stat_names = {f.name: None for f in fields(Stats) if True}

    # # name_input = ui.input("Name")
    # for stat in stat_names:
    #     pass
    


    # print(stat_names)
    # def create_character():

    #     stats = Stats(
    #         size=size_input.value,
    #         strength=strength_input.value,
    #         agility=agility_input.value,
    #         energy=energy_input.value,
    #         mana=mana_input.value
    #     )

    #     creature = Creature(
    #         name=name_input.value,
    #         stats=stats
    #     )

    #     creature.save()

    #     status_label.set_text(f"{creature.name} created!")

    # ui.button("Create Character", on_click=create_character)





# INDIVIDUAL CHARACTER PAGE
@ui.page('/character/{name}')
def character_page(name: str):

    character = Creature.load(name)

    ui.label(f'Character: {name}').classes('text-h4')

    ui.button(
        'Back to Characters',
        on_click=lambda: ui.navigate.to('/characters')
    )

    ui.label("Character Info")

    ui.label(f"stats: {class_to_text(character.stats)}")

    ui.button("Inventory", on_click=lambda: ui.navigate.to(f'/character/{name}/inventory'))

    ui.button("Attack", on_click=lambda: ui.navigate.to(f'/character/{name}/attack'))


@ui.page('/character/{name}/inventory')
def inventory_page(name: str):

    # data = Creature.load(name)
    # print(name)

    ui.label(f'{name} Inventory').classes('text-h4')

    ui.button(
        'Back to Character',
        on_click=lambda: ui.navigate.to(f'/character/{name}')
    )

    ui.label("We don't really have an inventory system yet.")

    # ui.label(f"stats: {class_to_text(data.stats)}")

    # ui.button("inventory")


@ui.page('/character/{name}/attack')
def attack_page(name: str):

    character = Creature.load(name)
    # print(name)

    ui.label(f'{name} Attack').classes('text-h4')

    ui.button(
        'Back to Character',
        on_click=lambda: ui.navigate.to(f'/character/{name}')
    )

    target_dict = selection_menu("Target", get_character_list(), filter_out=name)

    weapon_dict = selection_menu("Weapon", [character.weapon.name])

    status_label = ui.label("")

    def attack(c):
        
        enemy_name = target_dict['value']

        enemy = Creature.load(enemy_name)

        dam = c.attack(enemy)

        text = f"{name} attacked {enemy_name} for {dam} damage! \n{enemy_name} is now at {enemy.stats.health} health."

        if enemy.stats.health<=0: text+=f"\n {enemy_name} has died!"

        status_label.set_text(text)


        return
        


    ui.label('-------------------------------')
    ui.button(
        'Attack',
        on_click=lambda c=character: attack(c)#c.attack(Creature.load(target_dict['value'])) #print(target_dict['value'])
    )

    """
    status_label = ui.label("")

    def create_character():
        Creature(
            char_name.value,
            Stats(**get_widget_values(char_stats))
        )

        status_label.set_text(f"{char_name.value} created")

    ui.button(
        "Create",
        on_click=create_character
    )"""

    # character.








ui.run()
# print(get_character_list())
