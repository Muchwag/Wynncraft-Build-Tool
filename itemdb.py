import json
import math
import random

weapons = ['Dagger', 'Bow', 'Spear', 'Relik', 'Wand']
armor = ["Helmet", "Chestplate", "Leggings", "Boots"]
base_damages = ['damage', 'earthDamage', 'thunderDamage', 'waterDamage', 'fireDamage', 'airDamage']
attack_speed_mod = {'SUPER_FAST': 6, 'VERY_FAST': 5, 'FAST': 4, 'NORMAL': 3, 'SLOW': 2, 'VERY_SLOW': 1,
                    'SUPER_SLOW': 0}
rollable_IDs = ['healthRegen', 'manaRegen', 'spellDamage', 'lifeSteal', 'manaSteal', 'xpBonus',
                'lootBonus', 'reflection', 'thorns', 'exploding', 'speed', 'attackSpeedBonus', 'poison', 'healthBonus',
                'soulPoints', 'emeraldStealing', 'healthRegenRaw', 'spellDamageRaw', 'damageBonusRaw', 'damageBonus',
                'bonusFireDamage', 'bonusWaterDamage', 'bonusAirDamage', 'bonusThunderDamage', 'bonusEarthDamage',
                'bonusFireDefense', 'bonusWaterDefense', 'bonusAirDefense', 'bonusThunderDefense', 'bonusEarthDefense',
                'spellCostPct1', 'spellCostRaw1', 'spellCostPct2',
                'spellCostRaw2', 'spellCostPct3', 'spellCostRaw3', 'spellCostPct4', 'spellCostRaw4']

reverse_IDs = ['spellCostPct1', 'spellCostRaw1', 'spellCostPct2', 'spellCostRaw2', 'spellCostPct3', 'spellCostRaw3',
               'spellCostPct4', 'spellCostRaw4']


def get_reqs(item):
    req = {"strength": 0, "dexterity": 0, "intelligence": 0, "defense": 0, "agility": 0}
    bonus_sp = {"strengthPoints": 0, "dexterityPoints": 0, "intelligencePoints": 0, "defensePoints": 0,
                "agilityPoints": 0}
    pos_sp_no_req = False
    no_req = False
    neg_sp_only = False
    no_sp = False
    for key in req.keys():
        if item[key] != 0:
            req[key] = item[key]
    for key in bonus_sp.keys():
        if item[key] != 0:
            bonus_sp[key] = item[key]

    if all([x == 0 for x in req.values()]):
        no_req = True
    if all([v < 0 for v in bonus_sp.values()]):
        neg_sp_only = True
    if all([v == 0 for v in bonus_sp.values()]):
        no_sp = True
    if (not all([v <= 0 for v in bonus_sp.values()])) and all([v == 0 for v in req.values()]):
        pos_sp_no_req = True

    return dict({'pos_sp_no_req': pos_sp_no_req, 'no_req': no_req, 'neg_sp_only': neg_sp_only, 'no_sp': no_sp})


class ItemDB:
    def __init__(self):
        self.all_items = {}

    def add_item_from_json(self, jsonObj):
        if "displayName" in jsonObj:  # "displayName" for renamed items
            jsonObj["name"] = jsonObj["displayName"]
            del jsonObj["displayName"]

        if "identified" not in jsonObj:  # Adding identified to ALL items (thx wynn api rlly coming in clutch)
            jsonObj["identified"] = False

        try:  # Accesory items have accessoryType instead of type so try is used
            if jsonObj['type'] in weapons:
                jsonObj['damages'] = {}
                for attr in base_damages:  # change damage to average damage
                    values = jsonObj[attr].split('-')
                    jsonObj['damages'][attr.replace("Damage", "")] = [float(values[0]),
                                                                      float((int(values[0]) + int(values[1])) / 2),
                                                                      float(values[1])]
                    del jsonObj[attr]

            jsonObj['attackSpeed'] = attack_speed_mod[
                jsonObj['attackSpeed']]  # changes string attack speed to modifier value

        except:
            pass

        if jsonObj['identified'] == False:  # on items without fixed IDs turns base ID to max ID
            for attr in rollable_IDs:
                if attr in reverse_IDs:
                    try:
                        if int(jsonObj[attr]) > 0:
                            jsonObj[attr] = int(
                                jsonObj[attr] * 0.3 + 0.5)  # Python base rounding is banker's rounding, thus jank form
                        if int(jsonObj[attr]) < 0:
                            jsonObj[attr] = math.ceil(abs(jsonObj[attr] * 1.3 + 0.5)) * -1
                    except:
                        pass
                else:
                    try:
                        if int(jsonObj[attr]) > 0:
                            jsonObj[attr] = int(jsonObj[attr] * 1.3 + 0.5)
                        if int(jsonObj[attr]) < 0:
                            jsonObj[attr] = math.ceil(abs(jsonObj[attr] * 0.7 + 0.5)) * -1
                    except:
                        pass

        if 'accessoryType' in jsonObj:  # turns accessoryType values to type instead
            jsonObj['type'] = jsonObj['accessoryType']
            del jsonObj['accessoryType']

        if jsonObj["type"] in weapons:
            jsonObj["equipType"] = "Weapon"
        elif jsonObj["type"] in armor:
            jsonObj["equipType"] = "Armor"
        else:
            jsonObj["equipType"] = "Accessory"

        jsonObj['req_info'] = get_reqs(jsonObj)

        item_name = jsonObj["name"]
        self.all_items[item_name] = jsonObj

    def add_json(self, jsonArray):
        for obj in jsonArray:
            self.add_item_from_json(obj)

    def get_item(self, name):
        return self.all_items[name]

    def get_random_item(self):
        return random.choice(list(self.all_items.values()))
