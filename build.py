import copy
import json
from itertools import permutations, combinations
from collections import OrderedDict
from math import floor, ceil
import build_types
import random

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
damagetype_to_sp = {"earth": "strength", "thunder": "dexterity", "water": "intelligence", "fire": "defense",
                    "air": "agility"}
sp_bonuses = {0: 0.0, 1: 0.01, 2: 0.02, 3: 0.029, 4: 0.039, 5: 0.049, 6: 0.058, 7: 0.067, 8: 0.077, 9: 0.086, 10: 0.095,
              11: 0.104, 12: 0.113, 13: 0.122, 14: 0.131, 15: 0.139, 16: 0.148, 17: 0.157, 18: 0.165, 19: 0.173,
              20: 0.182, 21: 0.19, 22: 0.198, 23: 0.206, 24: 0.214, 25: 0.222, 26: 0.23, 27: 0.238, 28: 0.246,
              29: 0.253, 30: 0.261, 31: 0.268, 32: 0.276, 33: 0.283, 34: 0.29, 35: 0.298, 36: 0.305, 37: 0.312,
              38: 0.319, 39: 0.326, 40: 0.333, 41: 0.34, 42: 0.346, 43: 0.353, 44: 0.36, 45: 0.366, 46: 0.373,
              47: 0.379, 48: 0.386, 49: 0.392, 50: 0.399, 51: 0.405, 52: 0.411, 53: 0.417, 54: 0.423, 55: 0.429,
              56: 0.435, 57: 0.441, 58: 0.447, 59: 0.453, 60: 0.458, 61: 0.464, 62: 0.47, 63: 0.475, 64: 0.481,
              65: 0.486, 66: 0.492, 67: 0.497, 68: 0.503, 69: 0.508, 70: 0.513, 71: 0.518, 72: 0.523, 73: 0.528,
              74: 0.533, 75: 0.538, 76: 0.543, 77: 0.548, 78: 0.553, 79: 0.558, 80: 0.563, 81: 0.568, 82: 0.572,
              83: 0.577, 84: 0.581, 85: 0.586, 86: 0.591, 87: 0.595, 88: 0.599, 89: 0.604, 90: 0.608, 91: 0.612,
              92: 0.617, 93: 0.621, 94: 0.625, 95: 0.629, 96: 0.633, 97: 0.638, 98: 0.642, 99: 0.646, 100: 0.65,
              101: 0.654, 102: 0.657, 103: 0.661, 104: 0.665, 105: 0.669, 106: 0.673, 107: 0.676, 108: 0.68, 109: 0.684,
              110: 0.687, 111: 0.691, 112: 0.694, 113: 0.698, 114: 0.701, 115: 0.705, 116: 0.708, 117: 0.712,
              118: 0.715, 119: 0.718, 120: 0.722, 121: 0.725, 122: 0.728, 123: 0.731, 124: 0.735, 125: 0.738,
              126: 0.741, 127: 0.744, 128: 0.747, 129: 0.75, 130: 0.753, 131: 0.756, 132: 0.759, 133: 0.762, 134: 0.765,
              135: 0.768, 136: 0.771, 137: 0.773, 138: 0.776, 139: 0.779, 140: 0.782, 141: 0.784, 142: 0.787, 143: 0.79,
              144: 0.792, 145: 0.795, 146: 0.798, 147: 0.8, 148: 0.803, 149: 0.805, 150: 0.808}

with open('powder_values.json', "r") as powder_file:
    powder_data = json.load(powder_file)
with open('rough_spell_values.json', "r") as rough_spell_info_file:
    rough_spell_data = json.load(rough_spell_info_file)
with open('set_bonus_values.json', "r") as set_bonus_file:
    set_bonus_data = json.load(set_bonus_file)

powder_file.close()
rough_spell_info_file.close()
set_bonus_file.close()


def constrict(val, min_val, max_val):
    return max(min_val, min(val, max_val))


def add_req(item_obj, sp_dict):
    for point_type, value in sp_dict.items():
        if item_obj[point_type] > sp_dict[point_type]:
            sp_dict[point_type] = item_obj[point_type]
    return sp_dict


def add_sp(item_obj, sp_dict):
    for point_type, value in sp_dict.items():
        sp_dict[point_type] += item_obj[point_type + "Points"]
    return sp_dict


class Build:
    def __init__(self, type_=None, playstyle_=None, attribute_=None):
        self.build_data = {}
        self.build_stats = {}
        self.level = 101
        self.remaining_sp = (self.level - 1) * 2  # 200 sp
        self.type = type_
        self.playstyle = playstyle_
        self.attribute = attribute_
        if (not (self.type and self.playstyle and self.attribute)):
            self.type = build_types.BuildTypes.SPELL
            self.playstyle = build_types.BuildPlaystyles.LIGHT
            self.attribute = build_types.BuildAttributes.OFFENSIVE
            print("set default values for build", self.type, self.playstyle, self.attribute)

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
        # output += "----DAMAGE----\n"
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

    def get_powdered_dmg(self, conversion):
        return self.build_data["Weapon"].calc_powdered_dmg(conversion)

    def calc_exact_dps(self):
        print(self.calc_equip())
        pass

    def calc_dps(self, fast=True):  # calculates the rough dps of the build efficiently
        if fast:
            stats, weap_damage = self.calc_stats()
        else:
            stats = self.calc_equip()
            print(stats)
        spell_speed_mod = attack_speed_mod[stats["attackSpeed"]]
        melee_speed_mod = attack_speed_mod[constrict(stats["attackSpeed"] + stats['attackSpeedBonus'], 0, 6)]

        print(stats)
        total_melee_dps = 0
        total_melee_hit = 0
        total_spell_hit = 0
        weap_type_str = self.build_data["Weapon"].to_json()["type"]
        spell_info = rough_spell_data[weap_type_str]
        powdered_dmg = self.get_powdered_dmg(spell_info["conversion"])

        # print(powdered_dmg)
        powdered_dmg = powdered_dmg[0]

        for dmg_type, dmg_amount in powdered_dmg.items():

            if dmg_type == "damage":  # neutral damage;
                multiplier = (1 + sp_bonuses[stats["dexterityAssigned"]]) + sp_bonuses[stats["strengthAssigned"]] + (
                        stats["damageBonus"] / 100)
                total_melee_hit += dmg_amount[1] * multiplier + (stats["damageBonusRaw"] + max(stats["poison"] / 3, 0))
                total_melee_dps += (dmg_amount[1] * multiplier + (stats["damageBonusRaw"])) * melee_speed_mod + max(
                    stats["poison"] / 3, 0)

                spell_multiplier = (1 + sp_bonuses[stats["dexterityAssigned"]]) + sp_bonuses[
                    stats["strengthAssigned"]] + (stats["spellDamage"] / 100)
                total_spell_hit += (dmg_amount[1] * spell_multiplier * spell_speed_mod * spell_info["spell_modifier"]) + \
                                   stats["spellDamageRaw"] * spell_info["spell_modifier"]
            else:  # elemental damage
                sp_name = damagetype_to_sp[dmg_type]
                sp_assigned = stats[sp_name + "Assigned"]
                multiplier = (1 + sp_bonuses[stats["dexterityAssigned"]] + sp_bonuses[stats["strengthAssigned"]] +
                              + sp_bonuses[sp_assigned] + (stats["damageBonus"] + stats[
                            "bonus" + dmg_type.capitalize() + "Damage"]) / 100)

                total_melee_hit += dmg_amount[1] * multiplier
                total_melee_dps += dmg_amount[1] * multiplier * melee_speed_mod

                spell_multiplier = (1 + sp_bonuses[stats["dexterityAssigned"]] + sp_bonuses[stats["strengthAssigned"]] +
                                    + sp_bonuses[sp_assigned] + (stats["spellDamage"] + stats[
                            "bonus" + dmg_type.capitalize() + "Damage"]) / 100)
                this_element_hit = dmg_amount[1] * spell_multiplier * spell_speed_mod * spell_info["spell_modifier"]
                total_spell_hit += this_element_hit
                # print(sp_name, spell_multiplier, "sp assigned", ( sp_assigned ), "this element hit", this_element_hit)
        # print(spell_info)
        spell_cost_pct = stats["spellCostPct" + str(spell_info["spell_num"])]
        spell_cost_raw = stats["spellCostRaw" + str(spell_info["spell_num"])]
        spell_cost = spell_info["cost"]
        int_reduction = sp_bonuses[stats["intelligenceAssigned"]]
        total_spell_cost = max(1, floor(
            ceil(spell_cost * (1 - int_reduction) + spell_cost_raw) * (1 + spell_cost_pct / 100)))

        # print("pct",spell_cost_pct,"raw",spell_cost_raw,"spellcost:",spell_cost,"spellcostaftercalc",total_spell_cost)
        # calculate the amount of spells that can be used in 1 cycle and divide by 4 (seconds)
        spells_per_sec = min((5 + 0.8 * min(stats["manaRegen"], 19) + max(stats["manaSteal"], 0)) / total_spell_cost,
                             10) / 4
        total_spell_dps = total_spell_hit * spells_per_sec

        # print("spell_hit", total_spell_hit,  "spells per sec",spells_per_sec,"new spell dps",total_spell_dps,"mana regen:", stats["manaRegen"],"mana steal:",stats["manaSteal"])

        # print("Melee Hit:", total_melee_hit)
        # Melee dps = (base_dmg) * (str_bonus + melee_dmg% + ele% + sp_bonus%) * (speed_mod )
        # neutral = (base_dmg) * (str_bonus + melee_dmg%) * (speed_mod) + (raw melee) + max((poison / 3), 0)

        return total_melee_dps, total_spell_dps

    def calc_damages(self):  # calculate the damage of each spell
        pass

    def calc_stats(self):  # calculate the stats of the build
        # print (self.build_data["Weapon"].calc_powdered_dmg())
        build_stats = {}
        weap_damage = self.build_data["Weapon"].to_json()["damages"].copy()
        for item in self.build_data.values():
            item_json = item.to_json()
            # print("calculating " + item.to_json()["name"])

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
                build_stats[skill + "Assigned"] = constrict(build_stats[skill] + build_stats[skill + "Points"], 0, 150)

        return build_stats, weap_damage

        # print(self.build_stats)

    # THIS IS CALLED BY calc_equip!!!!!!!!!!!!!!!

    def good_equip(self):
        # Used to run every combo of item orders
        permutate_list = []
        # Points the permutations will start with (ex. no req items with pos sp don't need to be permutated)
        starting_points = {"strength": 0, "dexterity": 0, "intelligence": 0, "defense": 0, "agility": 0}
        weapon_points = {"strength": 0, "dexterity": 0, "intelligence": 0, "defense": 0, "agility": 0}
        # Points added at the end (items with all negative points can always go last)
        last_points = {"strength": 0, "dexterity": 0, "intelligence": 0, "defense": 0, "agility": 0}
        # Total sp req of the build
        req = {"strength": 0, "dexterity": 0, "intelligence": 0, "defense": 0, "agility": 0}
        for category, item in self.build_data.items():
            item = item.to_json()
            # Req info added in the itemDB, decided what kind of item it is for speed purposes.
            if not item['req_info']['no_req']:
                req = add_req(item, req)
            if item['type'] != 'Weapon':
                if item['req_info']['pos_sp_no_req']:
                    for point_type, value in starting_points.items():
                        starting_points[point_type] += item[point_type + "Points"]
                elif item['req_info']['neg_sp_only']:
                    for point_type, value in starting_points.items():
                        starting_points[point_type] += item[point_type + "Points"]
                elif not item['req_info']['no_sp']:
                    permutate_list.append(item)
            else:
                weapon_points = add_sp(item, weapon_points)

        best_set_remaining = 99999  # super high because any build will beat this first try
        best_set = {}
        for test_set in permutations(permutate_list, len(permutate_list)):
            set_points = starting_points.copy()
            assigned_points = {"strength": 0, "dexterity": 0, "intelligence": 0, "defense": 0, "agility": 0} # Tracks assigned points on the test

            for item in test_set:
                # Adding normal skill points from items
                for point_type, value in set_points.items():
                    if item[point_type] > value and item[point_type] != 0:  # 0 is default req (none) so we ignore them
                        # Updating total assigned (can't be over 100 or 200 overall)
                        assigned_points[point_type] += item[point_type] - set_points[point_type]
                        # Updating the set points and adding bonus from the item
                        set_points[point_type] = item[point_type]
                    set_points[point_type] += item[point_type + "Points"]

            # Adding last_points (usually negative sp)
            for point_type, value in last_points.items():
                set_points[point_type] += last_points[point_type]
                if set_points[point_type] < req[point_type] and req[point_type] != 0:
                    assigned_points[point_type] += req[point_type] - set_points[point_type]
                    set_points[point_type] = req[point_type]

            if any(x > 100 for x in assigned_points.values()) or sum(assigned_points.values()) > self.remaining_sp:
                # Impossible Build
                pass

            elif sum(assigned_points.values()) < best_set_remaining:
                for item in test_set:
                    print(item['name'], end=' ')
                print('is the best set')
                best_set_remaining = sum(assigned_points.values())
                best_set = set_points

        # Adding weapon points
        for point_type, value in starting_points.items():
            best_set[point_type] += weapon_points[point_type]
        print('BEST SET:', best_set)

        return best_set

    def equip_build(self, gear_set, total_req, starting_sp):
        best_set_stats = {"strength": 0, "dexterity": 0, "intelligence": 0, "defense": 0, "agility": 0,
                          'assigned': 99999}
        best_assigned = {}
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

                    if item[attr] > req[attr]:  # updates the total reqs of the build
                        req[attr] = item[attr]

                    points[attr] += item[attr + "Points"]  # adds item skill point bonuses

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
                best_assigned = assigned.copy()

        # weapon_json = self.build_data["Weapon"].to_json() # Add weapons sp to the final value
        # for skill in skill_req:
        #     best_set_stats[skill] += weapon_json[skill + "Points"]
        print({**{key + "Assigned": value for key, value in best_assigned.items()}, **best_set_stats})
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

            if not_pos_sp_reqless:  # checks if the item is reqless and only positive sp
                not_pos_sp_reqless = False  # first set it to be like vaward
                for skill in skill_req:
                    if item_json[skill] != 0 or item_json[
                        skill + "Points"] < 0:  # if it finds a req or -sp, then it will stop the loop
                        print("marking", item_json["name"], "as not positive sp reqless")

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
        # print(gear_set)
        # print(total_req)
        # print(starting_sp)
        return self.equip_build(gear_set, total_req, starting_sp)

    def get_set_sp(self, gear_set):

        pass


class Item:
    def __init__(self, itemjson):
        self.item_json = itemjson
        self.item_json["powders"] = []

    def __str__(self):
        return self.item_json["name"]

    def add_lists(self, list1, list2):  # creates new list
        return [x + y for x, y in zip(list1, list2)]

    def multi_list_by_const(self, list1, const):
        return [x * const for x in list1]

    def floor_recalculate_avg(self, damages):
        a = floor(damages[0])
        b = floor(damages[2])
        return [a, (a + b) / 2, b]

    def set_powders(self, powder_list):  # set powder like ["w6", "w6"]
        if len(powder_list) > self.item_json['sockets']:  # Checks if amount of powders is more than supported on item
            self.item_json["powders"] = powder_list[:self.item_json['sockets']]  # Uses indexing to find powders
            print("Failed to add", str(powder_list[self.item_json['sockets']:]), "item only supports",
                  self.item_json['sockets'], "powders")
        else:
            self.item_json["powders"] = powder_list  # If amount <= than supported on item, just applies adds them on

    def calc_powdered_dmg(self, conversion_values={}):
        conversion_values = {x: y for x, y in conversion_values.items() if y != 0}
        conversion_values = OrderedDict(conversion_values)
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
            conversion_sum = sum(conversion_values.values())
            for convert_element, convert_value in conversion_values.items():  # use the calculated conversion values and update neutral and the element
                convert_damage = self.multi_list_by_const(weapon_dmgs["damage"], convert_value)
                # new_neutral =   self.multi_list_by_const(weapon_dmgs["damage"], 1 - convert_value)
                weapon_dmgs[convert_element] = self.add_lists(weapon_dmgs[convert_element], convert_damage)
            weapon_dmgs["damage"] = self.multi_list_by_const(weapon_dmgs["damage"], 1 - conversion_sum)
            for dmg, dmg_list in weapon_dmgs.items():  # floor all values and recalculate the average
                weapon_dmgs[dmg] = self.floor_recalculate_avg(dmg_list)
            return weapon_dmgs, conversion_values
        else:
            raise SyntaxError("tried to calculate powdered damage on armor piece")

    def to_json(self):
        return self.item_json
