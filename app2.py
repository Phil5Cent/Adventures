from dataclasses import asdict, fields
import os
from fastapi import Request
from nicegui import ui
from urllib.parse import urlparse
from Combat_Testing import Creature, Stats

"""
TO DO/IDEAS

MAYBE WE CAN JUST HAVE A FEW PAGE TYPES. Like Navigation Page for character or inventory or whatever, 
or Creation Page (where you have info to be filled in) like the character page.

I also need a way that buttons can work that aren't just navigation buttons. Like buttons for navigation are good for directory, 
but if I wanted to activate a necklaces ability or something, it should call a function instead or something that would modify
the player's attributes. 










"""

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


def create_page(info, prev_path, current_path): #takes in custom info.
    
    ui.label(info["title"]).classes('text-4xl')

    ui.button(
    'Back',
    on_click=lambda: ui.navigate.to(prev_path)) #PREVIOUS LINK

    for key, value in info["data"].items():
        ui.label(key).classes('text-xl')
        ui.label(value).classes('text-base')
    
    for key, value in info["buttons"].items():
        ui.button(key, on_click=lambda x=value: ui.navigate.to(current_path + f'/{x}'))#FOLLOW UP LINK

    return



# MAIN MENU
@ui.page('/')
def main_menu():

    # info = {
    # "title": "Main Menu",

    # # "data": {
    #     # "Stats": class_to_text(self.stats)},

    # "buttons":{ #Display name and then page redirect name
    #     "Attack":"attack",
    #     "Inventory":"inventory",
    #     "Abilities":"abilities"
    #     }
    #     }
    

    ui.label('Main Menu').classes('text-h4')

    ui.button(
        'Characters',
        on_click=lambda: ui.navigate.to('/characters')
    )

    ui.button(
        'World',
        on_click=lambda: ui.navigate.to('/')
    )

    ui.button(
        'Other IDK',
        on_click=lambda: ui.navigate.to('/')
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



# INDIVIDUAL CHARACTER PAGE
@ui.page('/character/{name}') 
def character_page(request: Request, name: str):

    character = Creature.load(name)

    info = character.get_page_info()

    current_path = request.url.path

    full_prev_path = request.headers.get('referer', '/')
    prev_path = urlparse(full_prev_path).path

    # current_path = ui.run_javascript('return window.location.pathname')

    # prev_path = ui.run_javascript('return new URL(document.referrer).pathname')
    
    create_page(info, prev_path, current_path)
    

    # ui.label(info["title"]).classes('text-4xl')

    
# def get_path_history():
#     # Use ui.session to store per-user history
#     if not hasattr(ui.session, 'path_history'):
#         ui.session.path_history = {'current': None, 'previous': None}
#     return ui.session.path_history
    
# def update_paths():
#     path_history = get_path_history()
#     current = ui.run_javascript('return window.location.pathname')
    
#     if current != path_history['current']:
#         path_history['previous'] = path_history['current']
#         path_history['current'] = current

#     return path_history['current'], path_history['previous']



@ui.page('/character/{name}/inventory')
def inventory_page(name: str):


    ui.label(f'{name} Inventory').classes('text-h4')

    ui.button(
        'Back to Character',
        on_click=lambda: ui.navigate.to(f'/character/{name}')
    )

    ui.label("We don't really have an inventory system yet.")



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







ui.run()
