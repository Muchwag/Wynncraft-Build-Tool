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
skill_req = ['strength', 'dexterity', 'intelligence', 'defense', 'agility']
skill_bonus = ['strengthPoints', 'dexterityPoints', 'intelligencePoints', 'defensePoints', 'agilityPoints']
element_short = {"e": "earth", "t": "thunder", "w": "water", "f": "fire", "a": "air"}

with open('powder_values.json', "r") as powder_file:
    powder_data = json.load(powder_file)


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
        self.calc_stats()

    def remove_item(self, category):  # Deletes item from specified slot
        try:
            del self.build_data[category]
        except KeyError:
            print(f'Cannot find slot {category}')

    def set_weapon_powders(self, powders):
        self.build_data["Weapon"].set_powders(powders)

    def get_powdered_dmg(self):
        return self.build_data["Weapon"].calc_powdered_dmg()

    def calc_damages(self):  # calculate the damage of each spell
        pass

    def calc_stats(self):  # calculate the stats of the build
        # print (self.build_data["Weapon"].calc_powdered_dmg())
        self.build_stats = {}
        for slot, item in self.build_data.items():
            print("calculating " + item.to_json()["name"])
            for identification in identifications:
                if identification not in self.build_stats:
                    self.build_stats[identification] = 0

                if identification in item.to_json():
                    self.build_stats[identification] += item.to_json()[identification]

        # print(self.build_stats)
    @staticmethod
    def test_order_gen(items):
        poss_item_combos = list(permutations(items, 2))
        required_sp = [ Build.calc_build_sp(combo) for combo in poss_item_combos]
        print(required_sp)

    def equip_build(self, gear_set, total_req):
        best_set_stats = {"strength": 0, "dexterity": 0, "intelligence": 0, "defense": 0, "agility": 0, "total": 0}
        for test_set in permutations(gear_set, len(gear_set)):
            possible = True
            points = {"strength": 0, "dexterity": 0, "intelligence": 0, "defense": 0, "agility": 0, "total": 0}
            assigned = {"strength": 0, "dexterity": 0, "intelligence": 0, "defense": 0, "agility": 0}
            req = {"strength": 0, "dexterity": 0, "intelligence": 0, "defense": 0, "agility": 0}

            for item in test_set:
                for attr in skill_req:

                    if item[attr] > points[attr]:
                        points["total"] += item[attr] - points[attr]
                        assigned[attr] += item[attr] - points[attr]
                        points[attr] += item[attr] - points[attr]

                    if item[attr] > req[attr]: # updates the total reqs of the build
                        req[attr] = item[attr]
                    points[attr] += item[attr + "Points"] # adds item skill point bonuses

                    for attr in skill_req: # checks if any items would pop
                        if req[attr] > points[attr] and req[attr] > 0:
                            points["total"] += req[attr] - points[attr]
                            assigned[attr] += req[attr] - points[attr]
                            points[attr] = req[attr]

            for attr in skill_req:
                if total_req[attr] > points[attr] and total_req[attr] != 0:
                    points["total"] += total_req[attr] - points[attr]
                    assigned[attr] += total_req[attr] - points[attr]
                points[attr] = total_req[attr]    
        
            # Seeing if build is possible
            for attr in skill_req:
                if assigned[attr] > 100:
                    possible = False
                    break
            # checking if current set better than old best
            if points["total"] > best_set_stats["total"] and self.remaining_sp - points["total"] >= 0 and possible == True:
                best_set_stats = points.copy()
            
        return best_set_stats
        
    def calc_equip(self):

        total_req = {"strength": 0, "dexterity": 0, "intelligence": 0, "defense": 0, "agility": 0}
        gear_set = []
        for category, item in self.build_data.items():
            item_json = item.to_json()
            for skill in skill_req:
                if item_json[skill] > total_req[skill]:
                    total_req[skill] = item_json[skill]
            for skill in skill_req:
                if item_json[skill + "Points"] != 0 and category != "Weapon":
                    gear_set.append(item_json)
                    break
        print(self.equip_build(gear_set, total_req))


    @staticmethod
    def calc_build_sp(item_list_ordered):
        build_skill_reqs = {}
        build_skill_bonuses = {}
        for item in item_list_ordered:
            print("Doing item:" ,item)
            item_json = item.to_json()
            for skill in skill_req:
                skill_bonus_str = skill + "Points"
                skill_bonus_amnt = item_json[skill_bonus_str]
                item_req = item_json[skill]
                
                #print("req",item_req,"skillbonusamont",skill_bonus_amnt)
                if skill not in build_skill_reqs: # set default value to 0
                    build_skill_reqs[skill] = 0
                if skill_bonus_str not in build_skill_bonuses: # set default value to 0
                    build_skill_bonuses[skill_bonus_str] = 0
                build_skill_bonus = build_skill_bonuses[skill_bonus_str]
                build_skill_req = build_skill_reqs[skill]
                if build_skill_req + build_skill_bonus < item_req: # if item's req is greater than current req + sp bonus, add it
                    build_skill_reqs[skill] = item_req - build_skill_bonus
                    build_skill_bonuses[skill_bonus_str] += skill_bonus_amnt
                #print("bonuses",build_skill_bonuses,"reqs",build_skill_reqs)
        
        return list(build_skill_reqs.values())

    #     def generate_build_order(self):
    #         item_list = []
    #         for category, item in self.build_data.items():
    #             item_json = item.to_json
    #             if category == "Weapon":
    #                 weapon = item.to_json()
    #                 for skill in skill_bonus: # Removes sp bonus from weapon
    #                     weapon[skill] = 0
    #                 pass
    #             for attr in skill_reqs:
    #                 if item_json[attr] != 0:
    #                     item_list.append(item_json)
    #                     break
    #                 for attr in skill_bonus:
    #                     if item_json[attr] != 0:
    #                         item_list.append(item_json)
    #                     break

    #         for current_set in itertools.permutations(item_list, len(item_list)).shuffle():
    #             current_set.append(weapon)
    #             Build.calc_build_sp(current_set)
        



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

