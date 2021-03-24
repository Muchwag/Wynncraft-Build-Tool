import copy
import json
from itertools import permutations, combinations

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
attack_speed_mod = {6: 4.3, 5: 3.1, 4: 2.5, 3: 2.05, 2: 1.5, 1: 0.83,
                  0: 0.51}
skill_req = ['strength', 'dexterity', 'intelligence', 'defense', 'agility']
skill_bonus = ['strengthPoints', 'dexterityPoints', 'intelligencePoints', 'defensePoints', 'agilityPoints']
element_short = {"e": "earth", "t": "thunder", "w": "water", "f": "fire", "a": "air"}
damagetype_to_sp = {"earth": "strength", "thunder": "dexterity", "water": "intelligence", "fire": "defense", "air": "agility"}

with open('powder_values.json', "r") as powder_file:
    powder_data = json.load(powder_file)

def constrict(val, min_val, max_val):
        return max( min_val, min(val, max_val) )
    

class Build:
    def __init__(self):
        self.build_data = {}
        self.build_stats = {}
        self.level = 101
        self.remaining_sp = (self.level - 1) * 2  # 200 sp

    def __str__(self):
        gear_index = ["Helmet", "Chestplate", "Leggings",
                      "Boots", "Ring", "Ring2", "Bracelet", "Necklace", "Weapon"]
        output = "----ITEMS----\n"
        for gear_type, item in self.build_data.items():
            item_powders = " "
            for p in item.item_json["powders"]:
                item_powders += p
            gear_index[gear_index.index(gear_type)] = item.item_json["name"] + item_powders
        for item in gear_index:
            output += item + "\n"
        output += "----STATS----\n"
        for attr, value in self.build_stats.items():
            if value != 0:
                output += f'{attr}: {value}\n'
        return output

    def add_item(self, item):
        item_copy = Item(copy.deepcopy(item))  # make a copy so it isn't affected in itemDB
        item_type = "Weapon" if item_copy.item_json["equipType"] == "Weapon" else item_copy.item_json["type"]
        if item_copy.item_json["type"] == "Ring" and "Ring" in self.build_data:
            self.build_data['Ring2'] = item_copy
        else:
            self.build_data[item_type] = item_copy

    def remove_item(self, category):  # Deletes item from specified slot
        try:
            del self.build_data[category]
        except KeyError:
            print(f'Cannot find slot {category}')

    def set_weapon_powders(self, powders):
        self.build_data["Weapon"].set_powders(powders)

    def get_powdered_dmg(self):
        return self.build_data["Weapon"].calc_powdered_dmg()
    
    def calc_rough_dps(self): # calculates the rough dps of the build efficiently
        stats, weap_damage = self.calc_stats()
        spell_speed_mod = attack_speed_mod[stats["attackSpeed"]]
        melee_speed_mod = attack_speed_mod[constrict(stats["attackSpeed"] + stats['attackSpeedBonus'], 0, 6)]
    
        print(weap_damage)
        sp_bonuses = {0: 0.0, 1: 0.01, 2: 0.02, 3: 0.029, 4: 0.039, 5: 0.049, 6: 0.058, 7: 0.067, 8: 0.077, 9: 0.086, 10: 0.095, 11: 0.104, 12: 0.113, 13: 0.122, 14: 0.131, 15: 0.139, 16: 0.148, 17: 0.157, 18: 0.165, 19: 0.173, 20: 0.182, 21: 0.19, 22: 0.198, 23: 0.206, 24: 0.214, 25: 0.222, 26: 0.23, 27: 0.238, 28: 0.246, 29: 0.253, 30: 0.261, 31: 0.268, 32: 0.276, 33: 0.283, 34: 0.29, 35: 0.298, 36: 0.305, 37: 0.312, 38: 0.319, 39: 0.326, 40: 0.333, 41: 0.34, 42: 0.346, 43: 0.353, 44: 0.36, 45: 0.366, 46: 0.373, 47: 0.379, 48: 0.386, 49: 0.392, 50: 0.399, 51: 0.405, 52: 0.411, 53: 0.417, 54: 0.423, 55: 0.429, 56: 0.435, 57: 0.441, 58: 0.447, 59: 0.453, 60: 0.458, 61: 0.464, 62: 0.47, 63: 0.475, 64: 0.481, 65: 0.486, 66: 0.492, 67: 0.497, 68: 0.503, 69: 0.508, 70: 0.513, 71: 0.518, 72: 0.523, 73: 0.528, 74: 0.533, 75: 0.538, 76: 0.543, 77: 0.548, 78: 0.553, 79: 0.558, 80: 0.563, 81: 0.568, 82: 0.572, 83: 0.577, 84: 0.581, 85: 0.586, 86: 0.591, 87: 0.595, 88: 0.599, 89: 0.604, 90: 0.608, 91: 0.612, 92: 0.617, 93: 0.621, 94: 0.625, 95: 0.629, 96: 0.633, 97: 0.638, 98: 0.642, 99: 0.646, 100: 0.65, 101: 0.654, 102: 0.657, 103: 0.661, 104: 0.665, 105: 0.669, 106: 0.673, 107: 0.676, 108: 0.68, 109: 0.684, 110: 0.687, 111: 0.691, 112: 0.694, 113: 0.698, 114: 0.701, 115: 0.705, 116: 0.708, 117: 0.712, 118: 0.715, 119: 0.718, 120: 0.722, 121: 0.725, 122: 0.728, 123: 0.731, 124: 0.735, 125: 0.738, 126: 0.741, 127: 0.744, 128: 0.747, 129: 0.75, 130: 0.753, 131: 0.756, 132: 0.759, 133: 0.762, 134: 0.765, 135: 0.768, 136: 0.771, 137: 0.773, 138: 0.776, 139: 0.779, 140: 0.782, 141: 0.784, 142: 0.787, 143: 0.79, 144: 0.792, 145: 0.795, 146: 0.798, 147: 0.8, 148: 0.803, 149: 0.805, 150: 0.808}
        for skill in skill_req: 
            assigned = stats[skill] + stats[skill + "Points"]
            sp_bonuses[skill] = assigned
            
        total_melee_dps = 0
        total_melee_hit = 0
        for dmg_type, dmg_amount in weap_damage.items(): 
            if dmg_type == "damage": # neutral damage;
                multiplier = (1 + sp_bonuses[stats["dexterity"]]) + sp_bonuses[stats["strength"]] + (stats["damageBonus"] / 100)
                total_melee_hit += dmg_amount[1] * multiplier + (stats["damageBonusRaw"] + max(stats["poison"] / 3, 0))
                total_melee_dps += (dmg_amount[1] * multiplier + (stats["damageBonusRaw"] + max(stats["poison"] / 3, 0))) * melee_speed_mod
            else: # elemental damage
                sp_name = damagetype_to_sp[dmg_type]
                sp_assigned = stats[sp_name + "Assigned"]
                multiplier = (1 + sp_bonuses[stats["dexterityAssigned"]] + sp_bonuses[stats["strengthAssigned"]] + 
                    + sp_bonuses[sp_assigned] + (stats["damageBonus"] + stats["bonus" + dmg_type.capitalize() + "Damage"])/100 )
                
                total_melee_hit += dmg_amount[1] * multiplier
                total_melee_dps += dmg_amount[1] * multiplier * melee_speed_mod
                print(sp_name, multiplier, "dex boost amount", ( sp_assigned ))
        # print("Melee Hit:", total_melee_hit)
        # Melee dps = (base_dmg) * (str_bonus + melee_dmg% + ele% + sp_bonus%) * (speed_mod )
        # neutral = (base_dmg) * (str_bonus + melee_dmg%) * (speed_mod) + (raw melee) + max((poison / 3), 0)


        return total_melee_dps

    def calc_damages(self):  # calculate the damage of each spell
        pass

    def calc_stats(self):  # calculate the stats of the build
        # print (self.build_data["Weapon"].calc_powdered_dmg())
        build_stats = {}
        weap_damage = self.build_data["Weapon"].to_json()["damages"].copy()
        for item in self.build_data.values():
            item_json = item.to_json()
            #print("calculating " + item.to_json()["name"])
            
            for identification in identifications + skill_bonus:
                if identification not in build_stats:
                    build_stats[identification] = 0

                if identification in item.to_json():
                    build_stats[identification] += item.to_json()[identification]
            for skill in skill_req:
                if skill not in build_stats:
                    build_stats[skill] = 0

                if build_stats[skill] < item_json[skill]:
                    build_stats[skill] = item_json[skill]
                build_stats[skill + "Assigned"] = constrict(  build_stats[skill] + build_stats[skill + "Points"], 0, 150)

        return build_stats, weap_damage

        # print(self.build_stats)

    def equip_build(self, gear_set, total_req, starting_sp):
        best_set_stats = {"strength": 0, "dexterity": 0, "intelligence": 0, "defense": 0, "agility": 0, 'assigned': 99999}
        for test_set in permutations(gear_set, len(gear_set)):
            possible = True
            points = starting_sp
            assigned = {"strength": 0, "dexterity": 0, "intelligence": 0, "defense": 0, "agility": 0}
            req = {"strength": 0, "dexterity": 0, "intelligence": 0, "defense": 0, "agility": 0}

            for item in test_set:
                for attr in skill_req:

                    if item[attr] > points[attr]:
                        assigned[attr] += item[attr] - points[attr]
                        points[attr] += item[attr] - points[attr]

                    if item[attr] > req[attr]: # updates the total reqs of the build
                        req[attr] = item[attr]
                        
                    points[attr] += item[attr + "Points"] # adds item skill point bonuses


                    # for attr in skill_req: # checks if any items would pop

                    #     if req[attr] > points[attr] and req[attr] > 0:
                    #         #points["total"] += req[attr] - points[attr]
                    #         assigned[attr] += req[attr] - points[attr]
                    #         points[attr] = req[attr]
                    if req[attr] > points[attr] and req[attr] > 0:
                        assigned[attr] += req[attr] - points[attr]
                        points[attr] = req[attr]

            for attr in skill_req:
                if total_req[attr] > points[attr] and total_req[attr] != 0:
                    assigned[attr] += total_req[attr] - points[attr]
                    points[attr] = total_req[attr]

            # Seeing if build is possible
            for attr in skill_req:
                if assigned[attr] > 100:
                    possible = False
                    break
            # checking if current set better than old best
            points_sum = sum(assigned.values())
            if points_sum < best_set_stats["assigned"] and self.remaining_sp - points_sum >= 0 and possible == True:
                points['assigned'] = points_sum
                best_set_stats = points.copy()    
        
        
        # weapon_json = self.build_data["Weapon"].to_json() # Add weapons sp to the final value
        # for skill in skill_req:
        #     best_set_stats[skill] += weapon_json[skill + "Points"]
        
        return best_set_stats
        
    def get_build_req(self):
        total_req = {"strength": 0, "dexterity": 0, "intelligence": 0, "defense": 0, "agility": 0}
        for item in self.build_data.values():
            item_json = item.to_json()
            for skill in skill_req:
                if total_req[skill] < item_json[skill]:
                    total_req[skill] = item_json[skill]
        return total_req


    def calc_equip(self):
        
        total_req = {"strength": 0, "dexterity": 0, "intelligence": 0, "defense": 0, "agility": 0}
        starting_sp = {"strength": 0, "dexterity": 0, "intelligence": 0, "defense": 0, "agility": 0}
        gear_set = []
        total_sp_bonus = self.remaining_sp

        for category, item in self.build_data.items():
            not_pos_sp_reqless = False
            item_json = item.to_json()

            for skill in skill_req:
                if item_json[skill] > total_req[skill]:
                    total_req[skill] = item_json[skill]

                if item_json[skill + "Points"] != 0 and category != "Weapon":
                    total_sp_bonus += min(item_json[skill + "Points"], 0)
                    not_pos_sp_reqless = True
            
            if not_pos_sp_reqless: # checks if the item is reqless and only positive sp
                not_pos_sp_reqless = False #  first set it to be like vaward
                for skill in skill_req:
                    if item_json[skill] != 0 or item_json[skill + "Points"] < 0: # if it finds a req or -sp, then it will stop the loop
                        print("marking",item_json["name"],"as not positive sp reqless")
            
                        not_pos_sp_reqless = True
                        break
                        
            if not_pos_sp_reqless:
                # print("adding",item_json["name"],"as item with sp and req")
                gear_set.append(item_json)
            elif category != "Weapon":
                # print("adding",item_json["name"],"as item with no req no -sp")
                for skill in skill_req:
                    starting_sp[skill] += item_json[skill + "Points"]
            

        if total_sp_bonus < sum(total_req.values()):
            pass
            # RETURN IMPOSSIBLE BUILD
        #print(gear_set)
        #print(total_req)
        #print(starting_sp)
        return self.equip_build(gear_set, total_req, starting_sp)


class Item:
    def __init__(self, itemjson):
        self.item_json = itemjson
        self.item_json["powders"] = []
    def __str__(self):
        return self.item_json["name"]

    def add_lists(self, list1, list2):  # creates new list
        return [x + y for x, y in zip(list1, list2)]

    def set_powders(self, powder_list):  # set powder like ["w6", "w6"]
        if len(powder_list) > self.item_json['sockets']:  # Checks if amount of powders is more than supported on item
            self.item_json["powders"] = powder_list[:self.item_json['sockets']]  # Uses indexing to find powders
            print("Failed to add", str(powder_list[self.item_json['sockets']:]), "item only supports",
                  self.item_json['sockets'], "powders")
        else:
            self.item_json["powders"] = powder_list  # If amount <= than supported on item, just applies adds them on

    def calc_powdered_dmg(self, conversion_values={}):
        if self.item_json["equipType"] == "Weapon":
            weapon_dmgs = copy.deepcopy(self.item_json["damages"])
            for powder in self.item_json["powders"]:

                element = element_short[powder[0]]
                tier = powder[1]
                powder_specific_data = powder_data[element][tier]

                base = powder_specific_data["base"]
                conversion = powder_specific_data["conversion"]
                conversion_sum = sum(conversion_values.values())  # float between 0 and 1
                if element not in conversion_values:
                    conversion_values[element] = 0
                if conversion_sum + conversion >= 1:  # if conversion exceeds 1, add the remaining value
                    conversion_values[element] += (1 - conversion_sum)
                else:  # if not, its regular
                    conversion_values[element] += conversion
                weapon_dmgs[element] = self.add_lists(base, weapon_dmgs[element])
            return weapon_dmgs, conversion_values
        else:
            raise SyntaxError("tried to calculate powdered damage on armor piece")

    def to_json(self):
        return self.item_json

