from dataclasses import dataclass, field, asdict
import json
import shutil
from pathlib import Path


#TO DO

def class_to_text(data):
    stats_dict = asdict(data)
    return ",\n".join(f"{k}:{v}" for k, v in stats_dict.items())


"""



Include different player attack types (speed versus strength versus accuracy). 
I'm thinking the player should be able to choose their distribution





LATER

Include different weapon attack types (like a pointed versus flat side of hammer).
It would probably make sense to have a "selection" of attacks, which could be easily input into the
UI later with stats alongside them. Then the player can choose which attack to select, and proceed
with the attack as normal. 

add randomness to everything lol
"""


class Armor():
    def __init__(self, name="armor", weight = 1.3, protection=1, crush=0.1,slash=0.6,pierce=0.3):
    
        self.name = name
        self.weight = weight
        self.protection=protection


        self.crush = crush
        self.slash = slash
        self.pierce = pierce
        assert(self.crush+self.slash+self.pierce==1) #Probability Distribution

        pass
    
    def get_defense(self):


        return Defense(self.crush*self.protection,self.pierce*self.protection,self.slash*self.protection)

@dataclass
class Defense():
    crush: float
    pierce: float
    slash: float    
    pass


class Weapon():
    def __init__(self, name="weapon", accuracy=0.8, weight = 1, crush=0.4,slash=0.3,pierce=0.3):
    
        self.name = name
        self.accuracy = accuracy

        self.weight = weight

        self.crush = crush
        self.slash = slash
        self.pierce = pierce
        assert(self.crush+self.slash+self.pierce==1) #Probability Distribution

        # For now just worry a bout a single attack type or this will become overcomplicated quickly

        # I don't know how I would implement weapon range, so lets ignore that
        pass
    
    def get_attack(self, rate, force):

        attack_rate = rate*self.weight

        damage = (force*self.weight*self.crush, force*self.pierce, force*self.slash) #crush pierce slash

        return Attack(attack_rate,damage[0],damage[1],damage[2])



class Creature():
        
        
    # 2 Sections
    # Label = ""
    #LABEL
    # label = ""

    #DISPLAYS
    # Displays = {"Stats": class_to_text, "Additional Info": "that's all"}


    #Stats

    #NON-STANDARD BUTTONS
    # Buttons = ["Inventory", "Attack", "Stats"]
    #Inventory
    #Attack
    #Stats
    
    """
        
    ui.label(f'Character: {name}').classes('text-h4')

    ui.button(
        'Back to Characters',
        on_click=lambda: ui.navigate.to('/characters')
    )

    ui.label("Character Info")

    ui.label(f"stats: {class_to_text(character.stats)}")

    ui.button("Inventory", on_click=lambda: ui.navigate.to(f'/character/{name}/inventory'))

    ui.button("Attack", on_click=lambda: ui.navigate.to(f'/character/{name}/attack'))
    """
    

    def __init__(self, name="creature", stats=None, armor=None, weapon=None):

        if stats is None:
            stats = Stats()

        if armor is None:
            armor = Armor()

        if weapon is None:
            weapon = Weapon()

        self.name = name
        self.stats = stats
        self.armor = armor
        self.weapon = weapon


  







        self.save()

        return
    
    def attack(self, target):

        atk = self.weapon.get_attack(self.stats.rate, self.stats.force)
        dfn = target.armor.get_defense()
        
        crush = max(0,atk.crush-dfn.crush) 
        pierce = max(0,atk.pierce-dfn.pierce) 
        slash = max(0,atk.slash-dfn.slash)
        


        print(atk)
        print(dfn)
        damage = crush + pierce + slash
        print(damage)

        target.hurt(self, damage)

        return damage
    
    def hurt(self, source, damage):

        self.stats.health -= damage
        print(f"{source.name} hurt {self.name} for {damage} damage!")
        print(f"{self.name} has gone from {self.stats.health+damage} to {self.stats.health} health")
        
        self.save()

        if self.stats.health<=0: 

            print(f"{self.name} has died.")

            source_path = Path(f"characters/{self.name}.json")
            
            graveyard_path = Path(f"characters/graveyard/{self.name}.json")

            graveyard_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.move(source_path, graveyard_path)
            
            pass



    def to_dict(self):
        return {
            "name": self.name,
            "stats": self.stats.__dict__,
            "armor": self.armor.__dict__,
            "weapon": self.weapon.__dict__
        }

    @staticmethod
    def from_dict(data):
        stats = Stats(**data["stats"])
        armor = Armor(**data["armor"])
        weapon = Weapon(**data["weapon"])
        return Creature(data["name"], stats, armor, weapon)

    def save(self):
        with open(f"characters/{self.name}.json", "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @staticmethod
    def load(name):
        with open(f"characters/{name}.json") as f:
            data = json.load(f)
        return Creature.from_dict(data)

    def get_page_info(self): #INFO FOR PAGE

        info = {
            "title": self.name,

            "data": {
                "Stats": class_to_text(self.stats)},

            "buttons":{ #Display name and then page redirect name
                "Attack":"attack",
                "Inventory":"inventory",
                "Abilities":"abilities"
                }
        }

        return info
    
    def get_actions(self):

        self.actions = ["Attack", "Inventory", "Abiltiies"]

        return self.actions


    
    # def set_target(self, target):
    #     self.target = target
    #     return
        

@dataclass
class Stats():
    size: float = field(default=1, metadata={"base": True})
    strength: float = field(default=1, metadata={"base": True})
    agility: float = field(default=1, metadata={"base": True})
    magic: float = field(default=1, metadata={"base": True})
    energy: float = 1
    max_health: float | None = None
    rate: float | None = None
    force: float | None = None
    health: float | None = None

    pass

    def __post_init__(self):
        if self.max_health is None:
            self.max_health = self.strength * self.size ** 2

        if self.rate is None:
            self.rate = (self.size ** 0.75) / self.agility

        if self.force is None:
            self.force = (self.size ** 2) * self.strength

        if self.health is None:
            self.health = self.max_health

# class stats():
#     def __init__(self, size=1, strength=1, agility=1, energy=1, mana=1):
#         self.size=size
#         self.strength=strength
#         self.agility=agility
#         self.energy=energy
#         self.mana=mana

#         self.max_health = (size**2)
#         self.rate = (size**0.75)/agility
#         self.force = (size**2)*strength
#         pass



        #DAMAGE SHOULD BE THE SUM OF CRUSH, PIERCE, AND SLASH.

#how should a spear behave versus a light hammer versus a sword versus a dagger?
@dataclass
class Attack():
    rate: float
    crush: float
    pierce: float
    slash: float    
    pass



def res(size,strength,agility):
        
    max_health = (size**2)
    speed = (size**0.75)/agility
    force = (size**2)*strength

    print(round(max_health,1), round(speed,1), round(force,1))
    return 



# human1 = Creature("human1")
# human1.save()

# human2 = Creature.load("human1")

# human2.name="human2"
# human2.save()


# human1.set_target(human2)

# a = stats()

# human = creature(1,1,1)

# human.attack()

# orc = creature(size=1.3,agility=0.9,strength=1.5)
# orc.weapon=weapon()
# orc.attack()


#A giant 10x your size should take like 5 turns, and have like 100x your health, and do like 
#A giant 3x your size should take like 2-2.5 turns, and have like 10x your health, and od like 