import copy
import json

types = ["Helmet", "Chestplate", "Leggings", "Boots", "Weapon"]
weapons = ['Dagger', 'Bow', 'Spear', 'Relik', 'Wand']
identifications = [
            'health', 'healthRegen', 'healthRegenRaw', 'healthBonus',
            'manaRegen', 'manaSteal',
            'spellDamage', 'spellDamageRaw',
            'damageBonus', 'damageBonusRaw',
            'bonusEarthDamage', 'bonusThunderDamage', 'bonusWaterDamage', 'bonusFireDamage', 'bonusAirDamage',
            'spellCostPct1', 'spellCostPct2', 'spellCostPct3', 'spellCostPct4',
            'spellCostRaw1', 'spellCostRaw2', 'spellCostRaw3', 'spellCostRaw4',
            'damage', 'earthDamage', 'thunderDamage', 'waterDamage', 'fireDamage', 'airDamage',
            'attackSpeed', 'attackSpeedBonus', 'poison'
]
element_short = {"e": "earth", "t": "thunder", "w": "water", "f": "fire", "a": "air"}



with open('powder_values.json', "r") as powder_file:
        powder_data = json.load(powder_file)

class Build: 
    def __init__(self):
        self.build_data = {}
        self.build_stats = {}
        self.level = 101
        self.remaining_sp = (self.level - 1) * 2 # 200 sp        

    def __str__(self):
        gear_index = ["Helmet", "Chestplate", "Leggings", 
        "Boots", "Ring", "Ring2", "Bracelet", "Necklace", "Weapon"]
        for gear_type, item in self.build_data.items():
            gear_index[gear_index.index(gear_type)] = item.item_json["name"]

        return str(gear_index)

    def add_item(self, item):
        item_copy = Item(copy.deepcopy(item)) # make a copy so it isnt affected in itemDB
        item_type = "Weapon" if item_copy.item_json["equipType"] == "Weapon" else item_copy.item_json["type"]
        if item_copy.item_json["type"] == "Ring" and "Ring" in self.build_data:
            self.build_data['Ring2'] = item_copy
        else:
            self.build_data[item_type] = item_copy 
        self.calc_stats()

    def remove_item(self, category): # Deletes item from specified slot
        try:
            del self.build_data[category]
        except KeyError:
            print(f'Cannot find slot {category}')
        
    def set_weapon_powders(self,powders):
        self.build_data["Weapon"].set_powders(powders)

    def get_powdered_dmg(self):
        return self.build_data["Weapon"].calc_powdered_dmg()

    def calc_damages(self): # calculate the damage of each spell
        pass

    def calc_stats(self): # calculate the stats of the build
        #print (self.build_data["Weapon"].calc_powdered_dmg())
        self.build_stats = {}
        for slot, item in self.build_data.items():
            print("calculating " + item.to_json()["name"])
            for id in identifications:
                if (id not in self.build_stats):
                    self.build_stats[id] = 0
                    
                if (id in item.to_json()):
                    self.build_stats[id] += item.to_json()[id]
                    
        print(self.build_stats)



class Item:
    def __init__(self, itemjson):
        self.item_json = itemjson
        self.item_json["powders"] = []
        pass

    def add_lists(self, list1, list2): # creates new list
        return [x + y for x, y in zip(list1, list2)]
    

    def set_powders(self, powder_list): # set powder like ["w6", "w6"]
        for i in range(len(powder_list)): 
            if i > self.item_json['sockets']: # checks if item can support that many powders.
                print("item cannot support these powders " + powder_list)
                break
            else:
                self.item_json["powders"] = powder_list

    def calc_powdered_dmg(self, conversion_values = {}):
        if self.item_json["equipType"] == "Weapon":
            weapon_dmgs = copy.deepcopy(self.item_json["damages"])
            for powder in self.item_json["powders"]:
                
                element = element_short[powder[0]]
                tier = powder[1]
                powder_specific_data = powder_data[element][tier]

                base = powder_specific_data["base"]
                conversion = powder_specific_data["conversion"]
                conversion_sum = sum(conversion_values.values()) # float between 0 and 1
                if (element not in conversion_values):
                    conversion_values[element] = 0
                if (conversion_sum + conversion >= 1):# if conversion exceeds 1, add the remaining value
                    conversion_values[element] += (1 - conversion_sum )
                else: # if not, its regular
                    conversion_values[element] += conversion
                weapon_dmgs[element] = self.add_lists(base, weapon_dmgs[element])
            return weapon_dmgs, conversion_values
        else: 
            raise SyntaxError("tried to calculate powdered damage on armor piece")

    def to_json(self):
        return self.item_json