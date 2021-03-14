import requests 
import json
import math
from itemdb import ItemDB
from build import Build

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
epic = Build()
epic.add_item(itemdb.get_item("Chakram"))
#epic.add_item(itemdb.get_item("Moon Pool Circlet"))
#epic.add_item(itemdb.get_item("Stratus"))
#epic.set_weapon_powders(["e6","e6", "t6"])
#epic.remove_item("Ring2")
#print(itemdb.get_item("Chakram"))
print(str(epic.build_stats))
#print("damages calculation: " + str(epic.get_powdered_dmg()))