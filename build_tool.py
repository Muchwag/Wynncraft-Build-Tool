import json
from itertools import permutations
import math

with open('ItemDict1.20.txt') as ItemDict:
    item_dict = json.load(ItemDict)
    ItemDict.close()


class Build:
    def __init__(self, input_build): 
        self.input = input_build.lower().split(', ')
        self.build = []
        self.possible = False
        self.possible_reason = []
        self.skill_points = {'unassigned': 0}
        self.stats = {}
        self.character = None
        self.powder = []
        self.output = ''
        self.spell_info = {}
        self.skill_point_bonus = {}
        self.spell_cost = {'spell1': '-', 'spell2': '-', 'spell3': '-', 'spell4': '-'}

        # DAMAGE SELF ATTRIBUTES
        self.melee_hit = 0
        self.melee_dps = 0

        self.spell1 = '-'
        self.spell2 = '-'
        self.spell3 = '-'
        self.spell4 = '-'

        # TURN QUERY INTO ITEM DICTS
        for item in self.input:
            if '[' in item:
                item = item.split('[')
                self.powder = item[1].replace(']', '').split('-')
                item = item[0]
            try:
                self.build.append(item_dict[item])
            except KeyError:
                print(item, 'not found!')
                continue

    # ADD HIVE AND ORNATE CHECKERS
    def Equippable(self):
        skill_point_set = []
        gear_count = {'Helmet': 0, 'Chestplate': 0, 'Leggings': 0, 'Boots': 0, 'Ring': 0, 'Bracelet': 0, 'Necklace': 0,
                      'Weapon': 0}
        for item in self.build:

            if 'type' in item:
                if item['type'] in ['Dagger', 'Bow', 'Wand', 'Spear', 'Relik']:
                    gear_count['Weapon'] += 1
                    self.character = item['type']
                else:
                    gear_count[item['type']] += 1

            elif 'accessoryType' in item:
                gear_count[item['accessoryType']] += 1

            for gear, count in gear_count.items():
                if gear != 'Ring' and count > 1:
                    self.possible = False
                    return
                elif gear != 'Ring' and count > 2:
                    self.possible = False
                    return

            for attr in [
                'strength', 'dexterity', 'intelligence', 'defense', 'agility',
                'strengthPoints', 'dexterityPoints', 'intelligencePoints', 'defensePoints', 'agilityPoints'
            ]:
                if item[attr] != 0:
                    skill_point_set.append(item)
                    break

        for test_set in permutations(skill_point_set, len(skill_point_set)):
            current_set_stats = {'skill_points': {}}
            possible = True
            skill_points = {
                'strength': 0, 'dexterity': 0, 'intelligence': 0, 'defense': 0, 'agility': 0,
                'strengthR': 0, 'dexterityR': 0, 'intelligenceR': 0, 'defenseR': 0, 'agilityR': 0,
                'strengthA': 0, 'dexterityA': 0, 'intelligenceA': 0, 'defenseA': 0, 'agilityA': 0,
                'assigned': 0
            }
            weapon_points = {'strength': 0, 'dexterity': 0, 'intelligence': 0, 'defense': 0, 'agility': 0}

            for item in test_set:
                for attr in ['strength', 'dexterity', 'intelligence', 'defense', 'agility']:

                    if item[attr] > skill_points[attr]:
                        skill_points['assigned'] += item[attr] - skill_points[attr]
                        skill_points[attr + 'A'] += item[attr] - skill_points[attr]
                        skill_points[attr] = item[attr]

                    if 'type' in item:
                        if item['type'] in ['Dagger', 'Bow', 'Wand', 'Spear', 'Relik']:
                            weapon_points[attr] += item[attr + 'Points']
                        else:
                            skill_points[attr] += item[attr + 'Points']
                    else:
                        skill_points[attr] += item[attr + 'Points']

            for attr in ['strengthA', 'dexterityA', 'intelligenceA', 'defenseA', 'agilityA']:
                if skill_points[attr] > 100:
                    possible = 'impossible'

            if skill_points['assigned'] > 200:
                possible = 'impossible'

            if possible:
                current_set_stats['possible'] = 'possible'
                for attr in ['strength', 'dexterity', 'intelligence', 'defense', 'agility']:
                    skill_points[attr] += weapon_points[attr]
                    current_set_stats['skill_points'][attr] = skill_points[attr]
                current_set_stats['skill_points']['unassigned'] = 200 - skill_points['assigned']

                for gear_type, value in gear_count.items():
                    if value > 1 and gear_type != 'Ring':
                        current_set_stats['possible'] = 'impossible'
                    elif value > 2 and gear_type == 'Ring':
                        current_set_stats['possible'] = 'impossible'

            if self.skill_points['unassigned'] < current_set_stats['skill_points']['unassigned']:
                self.skill_points = current_set_stats['skill_points']
                self.possible = current_set_stats['possible']

    def Stats(self):

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
        for id in identifications:
            self.stats[id] = 0

        for item in self.build:
            for attr in list(item):
                if attr == 'sockets':
                    if 'type' in item:
                        if item['type'] in ['Dagger', 'Bow', 'Wand', 'Spear', 'Relik']:
                            self.stats['sockets'] = item['sockets']

                if attr in identifications:
                    if attr in [
                        'health', 'healthRegen', 'healthRegenRaw', 'healthBonus',
                        'manaRegen', 'manaSteal',
                        'spellDamageRaw', 'damageBonusRaw',
                        'damage', 'earthDamage', 'thunderDamage', 'waterDamage', 'fireDamage', 'airDamage',
                        'attackSpeed', 'attackSpeedBonus', 'poison'
                    ]:
                        self.stats[attr] += item[attr]
                    else:
                        self.stats[attr] += item[attr] / 100

    def Damage(self):

        if not self.possible:
            return

        spell_info = {
            'Dagger':
                {
                    'spell1':
                        {'conversions': {'earth': 0, 'thunder': 0.3, 'water': 0, 'fire': 0, 'air': 0},
                         'modifier': 1.5, 'name': ':dizzy:', 'cost': 6, 'NormalCalc': True},
                    'spell2':
                        {'conversions': {'earth': 0, 'thunder': 0, 'water': 0, 'fire': 0, 'air': 0},
                         'modifier': 0, 'name': ':detective:', 'cost': 2, 'NormalCalc': True},
                    'spell3':
                        {'conversions': {'earth': 0, 'thunder': 0.0923076923, 'water': 0.1538461538, 'fire': 0, 'air': 0},
                         'modifier': 3.9, 'name': ':loop:', 'cost': 8, 'NormalCalc': True},
                    'spell4':
                        {'conversions': {'earth': 0.25, 'thunder': 0, 'water': 0, 'fire': 0, 'air': 0.25},
                         'modifier': 6.0, 'name': ':bomb:', 'cost': 8, 'NormalCalc': True}

                },
            'Bow':
                {
                    'spell1':
                        {'conversions': {'earth': 0, 'thunder': 0.25, 'water': 0, 'fire': 0.15, 'air': 0},
                         'modifier': 6.0, 'name': ':bow_and_arrow:', 'cost': 6, 'NormalCalc': True},
                    'spell2':
                        {'conversions': {'earth': 0, 'thunder': 0, 'water': 0, 'fire': 0, 'air': 0.5},
                         'modifier': 1, 'name': ':parachute:', 'cost': 3, 'NormalCalc': True},
                    'spell3':
                        {'conversions': {'earth': 0.25, 'thunder': 0, 'water': 0, 'fire': 0.15, 'air': 0},
                         'modifier': 2.5, 'name': ':dash:', 'cost': 8, 'NormalCalc': True},
                    'spell4':
                        {'conversions': {'earth': 0, 'thunder': 0, 'water': 0.3, 'fire': 0, 'air': 0},
                         'modifier': 1, 'name': ':shield:', 'cost': 10, 'NormalCalc': True}

                },
            'Spear':
                {
                    'spell1':
                        {'conversions': {'earth': 0.4, 'thunder': 0, 'water': 0, 'fire': 0, 'air': 0},
                         'modifier': 2.6, 'name': ':boxing_glove:', 'cost': 6, 'NormalCalc': True},
                    'spell2':
                        {'conversions': {'earth': 0, 'thunder': 0, 'water': 0, 'fire': 0.4, 'air': 0.5},
                         'modifier': 1.5, 'name': ':sparkler:', 'cost': 4, 'NormalCalc': True},
                    'spell3':
                        {'conversions': {'earth': 0.15, 'thunder': 0, 'water': 0, 'fire': 0, 'air': 0},
                         'modifier': 4.0, 'name': ':muscle:', 'cost': 10, 'NormalCalc': True},
                    'spell4':
                        {'conversions': {'earth': 0, 'thunder': 0, 'water': 0, 'fire': 0.25, 'air': 0.75},
                         'modifier': 1, 'name': ':anger_right:', 'cost': 6, 'NormalCalc': True}

                },
            'Wand':
                {
                    'spell1':
                        {'conversions': {'earth': 0, 'thunder': 0, 'water': 0, 'fire': 0, 'air': 0},
                         'modifier': 0, 'name': ':heart:', 'cost': 6, 'NormalCalc': False},
                    'spell2':
                        {'conversions': {'earth': 0, 'thunder': 0.4, 'water': 0, 'fire': 0, 'air': 0},
                         'modifier': 1, 'name': ':levitate:', 'cost': 4, 'NormalCalc': True},
                    'spell3':
                        {'conversions': {'earth': 0.3, 'thunder': 0, 'water': 0, 'fire': 0.3, 'air': 0},
                         'modifier': 5.0, 'name': ':comet:', 'cost': 8, 'NormalCalc': True},
                    'spell4':
                        {'conversions': {'earth': 0, 'thunder': 0, 'water': 0.5, 'fire': 0, 'air': 0},
                         'modifier': 0.7, 'name': ':snake:', 'cost': 4, 'NormalCalc': True}

                },
            'Relik':
                {
                    'spell1':
                        {'conversions': {'earth': 0, 'thunder': 0, 'water': 0, 'fire': 0.2, 'air': 0.2},
                         'modifier': 1, 'name': ':moyai:', 'cost': 4, 'NormalCalc': True},
                    'spell2':
                        {'conversions': {'earth': 0, 'thunder': 0, 'water': 0, 'fire': 0.4, 'air': 0.5},
                         'modifier': 1.5, 'name': ':person_doing_cartwheel:', 'cost': 1, 'NormalCalc': True},
                    'spell3':
                        {'conversions': {'earth': 0, 'thunder': 0, 'water': 0.3, 'fire': 0, 'air': 0},
                         'modifier': 2.0, 'name': ':spiral:', 'cost': 8, 'NormalCalc': True},
                    'spell4':
                        {'conversions': {'earth': 0.3, 'thunder': 0, 'water': 0, 'fire': 0, 'air': 0},
                         'modifier': 0.75, 'name': ':anger_right:', 'cost': 6, 'NormalCalc': True}

                },
            None:
                {
                    'spell1':
                        {'conversions': {'earth': 0, 'thunder': 0, 'water': 0, 'fire': 0, 'air': 0},
                         'modifier': 0, 'name': ':no_entry:', 'cost': 0, 'NormalCalc': True},
                    'spell2':
                        {'conversions': {'earth': 0, 'thunder': 0, 'water': 0, 'fire': 0, 'air': 0},
                         'modifier': 0, 'name': ':no_entry:', 'cost': 0, 'NormalCalc': True},
                    'spell3':
                        {'conversions': {'earth': 0, 'thunder': 0, 'water': 0, 'fire': 0, 'air': 0},
                         'modifier': 0, 'name': ':no_entry:', 'cost': 0, 'NormalCalc': True},
                    'spell4':
                        {'conversions': {'earth': 0, 'thunder': 0, 'water': 0, 'fire': 0, 'air': 0},
                         'modifier': 0, 'name': ':no_entry:', 'cost': 0, 'NormalCalc': True}

                }
        }
        self.spell_info = spell_info[self.character]

        powder_base = {'e': 20, 't': 22.5, 'w': 15, 'f': 17, 'a': 17}
        powder_mod = {'e': 0.46, 't': 0.28, 'w': 0.32, 'f': 0.37, 'a': 0.35}
        powder_name = {'e': 'earth', 't': 'thunder', 'w': 'water', 'f': 'fire', 'a': 'air'}

        stats = self.stats.copy()

        self.skill_point_bonus = {}
        for skill in self.skill_points:
            self.skill_point_bonus[skill + 'Bonus'] = round((-0.0000000166 * (
                    self.skill_points[skill] ** 4) + 0.0000122614 * (
                                                                self.skill_points[skill] ** 3) - 0.0044972984 *
                                                        (self.skill_points[skill] ** 2) + 0.9931907398 *
                                                        self.skill_points[skill] + 0.0093811967) / 100, 3)

            self.skill_point_bonus[skill + 'Bonus'] = min(max(0, self.skill_point_bonus[skill + 'Bonus']), 0.808)

        if self.character is None:
            self.melee_hit = 0
            self.melee_dps = 0
            self.spell1 = 0
            self.spell2 = 0
            self.spell3 = 0
            self.spell4 = 0
            return

        attack_speed_mods = [0.51, 0.83, 1.5, 2.05, 2.5, 3.1, 4.3]

        conversions = {'earth': 0, 'thunder': 0, 'water': 0, 'fire': 0, 'air': 0}
        conversion_amount = 0

        for i in range(stats['sockets']):
            if i >= len(self.powder):
                break
            if conversion_amount < 1:
                conversions[powder_name[self.powder[i]]] += powder_mod[self.powder[i]]
                conversion_amount += powder_mod[self.powder[i]]

                if conversion_amount > 1:
                    conversions[powder_name[self.powder[i]]] -= conversion_amount - 1
                    conversion_amount = 1

            stats[powder_name[self.powder[i]] + 'Damage'] += powder_base[self.powder[i]]
        # MELEE DAMAGE

        for element, value in conversions.items():
            stats[element + 'Damage'] += stats['damage'] * value
            stats['damage'] -= stats['damage'] * value
        self.melee_hit = int(((1 * (1 + self.skill_point_bonus['dexterityBonus'])) + stats['damageBonus']) * stats['damage'])

        for element, skill in {'earth': 'strengthBonus', 'thunder': 'dexterityBonus', 'water': 'intelligenceBonus',
                               'fire': 'defenseBonus', 'air': 'agilityBonus'}.items():
            self.melee_hit += int(((1 * (1 + self.skill_point_bonus['dexterityBonus'])) + self.skill_point_bonus[
                'strengthBonus'] + stats['bonus' + element.capitalize() + 'Damage'] +
                                   stats['damageBonus'] + self.skill_point_bonus[skill]) * stats[element + 'Damage'])
        self.melee_hit += stats['damageBonusRaw'] + (stats['poison'] / 3)

        self.melee_hit = int(self.melee_hit)
        self.melee_dps = int(self.melee_hit * attack_speed_mods[
            min(max(attack_speed_mods.index(stats['attackSpeed']) + stats['attackSpeedBonus'], 0), 6)])

        # SPELL DAMAGE

        for current_spell in ['spell1', 'spell2', 'spell3', 'spell4']:
            stats = self.stats.copy()
            spell_stats = spell_info[self.character][current_spell].copy()
            conversions = {'earth': 0, 'thunder': 0, 'water': 0, 'fire': 0, 'air': 0}
            conversion_amount = 0

            if self.spell_info[current_spell]['NormalCalc']:

                for element, value in spell_info[self.character][current_spell]['conversions'].items():
                    conversions[element] += value
                    conversion_amount += value

                for i in range(stats['sockets']):
                    if i >= len(self.powder):
                        break
                    if conversion_amount < 1:
                        conversions[powder_name[self.powder[i]]] += powder_mod[self.powder[i]]
                        conversion_amount += powder_mod[self.powder[i]]

                        if conversion_amount > 1:
                            conversions[powder_name[self.powder[i]]] -= conversion_amount - 1
                            conversion_amount = 1

                    stats[powder_name[self.powder[i]] + 'Damage'] += powder_base[self.powder[i]]

                for element, value in conversions.items():
                    stats[element + 'Damage'] += stats['damage'] * value
                    stats['damage'] -= stats['damage'] * value

                spell_damage = int(((1 * (1 + self.skill_point_bonus['dexterityBonus'])) + self.skill_point_bonus['strengthBonus'] +
                                    stats['spellDamage']) * int(stats['damage']) * stats['attackSpeed'] * spell_stats[
                                       'modifier'])
                for element, skill in {'earth': 'strengthBonus', 'thunder': 'dexterityBonus', 'water': 'intelligenceBonus',
                                       'fire': 'defenseBonus', 'air': 'agilityBonus'}.items():

                    spell_damage += int(
                        ((1 * (1 + self.skill_point_bonus['dexterityBonus'])) + self.skill_point_bonus['strengthBonus'] +
                         stats['bonus' + element.capitalize() + 'Damage'] + stats['spellDamage'] +
                         self.skill_point_bonus[skill]) * int(stats[element + 'Damage']) * stats['attackSpeed'] *
                        spell_stats['modifier'])

                spell_damage += stats['spellDamageRaw'] * spell_stats['modifier']

                if current_spell == 'spell1':
                    self.spell1 = int(spell_damage)
                elif current_spell == 'spell2':
                    self.spell2 = int(spell_damage)
                elif current_spell == 'spell3':
                    self.spell3 = int(spell_damage)
                elif current_spell == 'spell4':
                    self.spell4 = int(spell_damage)

            else:
                if self.spell_info[current_spell]['name'] == ':heart:':
                    heal_amount = ((max(stats['health'] + stats['healthBonus'] + 535, 5)) * 0.24) * (
                                1 + (stats['bonusWaterDamage']) / 2)

                    self.spell1 = int(heal_amount)

            self.SpellCost()

    def SpellCost(self):
        if not self.possible:
            return

        spellType = {'spell1': ['spellCostPct1', 'spellCostRaw1'],
                     'spell2': ['spellCostPct2', 'spellCostRaw2'],
                     'spell3': ['spellCostPct3', 'spellCostRaw3'],
                     'spell4': ['spellCostPct4', 'spellCostRaw4']}
        for spell in ['spell1', 'spell2', 'spell3', 'spell4']:
            finalCost = int(math.ceil(self.spell_info[spell]['cost'] * (1 - self.skill_point_bonus['intelligenceBonus'])) + self.stats[spellType[spell][1]] * (1 + self.stats[spellType[spell][0]] / 100))

            if finalCost < 1:
                finalCost = 1
            self.spell_cost[spell] = finalCost

    def Print(self):
        spell1 = self.spell_info['spell1']['name']
        spell2 = self.spell_info['spell2']['name']
        spell3 = self.spell_info['spell3']['name']
        spell4 = self.spell_info['spell4']['name']

        spellcost1 = self.spell_cost['spell1']
        spellcost2 = self.spell_cost['spell2']
        spellcost3 = self.spell_cost['spell3']
        spellcost4 = self.spell_cost['spell4']

        str = self.skill_points['strength']
        dex = self.skill_points['dexterity']
        int = self.skill_points['intelligence']
        enc = self.skill_points['defense']
        agi = self.skill_points['agility']
        extraSP = self.skill_points['unassigned']

        possibility = ''
        for x in self.possible_reason:
            possibility += x + '\n'

        HP = max(self.stats['health'] + self.stats['healthBonus'] + 535, 5)
        MR = self.stats['manaRegen']
        MS = self.stats['manaSteal']

        self.output = f'I AM ATLAS BOT\n\
--------------------\n\
this build is {self.possible}\n\n\
{possibility}\
:green_circle: {str} - :yellow_circle: {dex} - :blue_circle: {int} - :red_circle: {enc} - :white_circle: {agi} - :no_entry_sign: {extraSP}\n\n\
STATS\n\
HP: {HP}\n\
Mana Regen: {MR}/4 - Mana Steal: {MS}/4\n\n\
DAMAGE\n\
:crossed_swords::   {self.melee_dps} ({self.melee_hit} per hit)\n\
{spell1}:   {self.spell1} :small_blue_diamond: {spellcost1}\n\
{spell2}:   {self.spell2} :small_blue_diamond: {spellcost2}\n\
{spell3}:   {self.spell3} :small_blue_diamond: {spellcost3}\n\
{spell4}:   {self.spell4} :small_blue_diamond: {spellcost4}'
        return self.output


def Main(content):
    build = Build(content)
    build.Equippable()
    build.Stats()
    build.Damage()
    return build.Print()
