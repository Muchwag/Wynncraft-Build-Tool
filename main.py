import requests 
import json
import math
from itemdb import ItemDB
from build import Build
from build import Item
import timeit

itemdb = ItemDB()

# importing wynn item DB for stashing 
def get_items():
    try: 
        with open('item_file.json', "r") as item_file:
            item_list = json.load(item_file)
            print("successfully loaded")
    except:
        request = requests.get('https://api.wynncraft.com/public_api.php?action=itemDB&category=all')
        item_list = request.json()['items']

    with open('item_file.json', "w") as item_file:
        json.dump(item_list, item_file)
    return item_list


itemdb.add_json(get_items())
#print(itemdb.get_item("Thrunda Ripsaw"))
epic = Build()
#epic.add_item(itemdb.get_item("Donner"))
epic.add_item(itemdb.get_item("Chakram"))
epic.set_weapon_powders(["w6","w6"])
print(epic.get_powdered_dmg())


# #print(epic.calc_equip())
# print("dps calculated",epic.calc_rough_dps())

setupStr = """
import requests 
import json
import math
from itemdb import ItemDB
from build import Build
from build import Item
itemdb = ItemDB()

# importing wynn item DB for stashing 
def get_items():
    try: 
        with open('item_file.json', "r") as item_file:
            item_list = json.load(item_file)
            print("successfully loaded")
    except:
        request = requests.get('https://api.wynncraft.com/public_api.php?action=itemDB&category=all')
        item_list = request.json()['items']

    with open('item_file.json', "w") as item_file:
        json.dump(item_list, item_file)
    return item_list
itemdb.add_json(get_items())
    
"""
runStr = """
epic = Build()
epic.add_item(itemdb.get_item("Moon Pool Circlet"))
epic.add_item(itemdb.get_item("Moon Pool Circlet"))
epic.add_item(itemdb.get_item("Aquarius"))
epic.add_item(itemdb.get_item("Seipodon"))
epic.add_item(itemdb.get_item("Capricorn"))
epic.add_item(itemdb.get_item("Gold Hydro Bracelet"))
epic.add_item(itemdb.get_item("Diamond Hydro Necklace"))
epic.add_item(itemdb.get_item("Third Eye"))
epic.calc_equip()
"""

num = 100
#print("time taken",timeit.timeit(stmt=runStr, setup=setupStr, number=num) / num) 