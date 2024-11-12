import requests
import time
#from helpers import _print_timer_line, id_item_dict
import save_system

id_item_dict = {
    0	: "Spurce log",
    1	: "Pine log",
    2	: "Chestnut log",
    6	: "Oak log",
    7	: "Maple log",
    8	: "Teak log",
    9	: "Mahogany log",
    10	: "Yew log",
    15	: "Raw carp",
    31	: "Coal ore",
    42	: "Titanium ore",
    46	: "Titanium bar",
    54	: "Normal hatchet",
    113	: "Raw superior meat",
    118	: "Nettle",
    122	: "Blueberry",
    125	: "Porcini",
    126	: "Potato seed",
    127	: "Carrot seed",
    128	: "Tomato seed",
    129	: "Cabbage seed",
    130	: "Strawberry seed",
    131	: "Watermelon seed",
    132	: "Potato",
    133	: "Carrot",
    134	: "Tomato",
    135	: "Cabbage",
    136	: "Strawberry",
    137	: "Watermelon",
    138	: "Onion",
    155	: "Raw anglerfish",
    156	: "Cooked anglerfish",
    157	: "Raw zander",
    158	: "Cooked zander",
    159	: "Raw piranha",
    160	: "Cooked piranha",
    161	: "Raw pufferfish",
    162	: "Cooked pufferfish",
    225	: "Refined gemstone",
    226	: "Great gemstone",
    227	: "Elite gemstone",
    228	: "Superior gemstone",
    229	: "Outstanding gemstone",
    230	: "Godlike gemstone",
    248	: "Red leather",
    265	: "Titanium arrow",
    266	: "Astronomical arrow",
    273	: "Magical flax",
    274	: "Enchanted flax",
    275	: "Cursed flax",
    337	: "Premium membership token",
    378	: "Diamond ore",
    399	: "Seaweed",
    400	: "Grape seed",
    401	: "Grape",
    402	: "Papaya seed",
    403	: "Papaya",
    404	: "Dragon fruit seed",
    405	: "Dragon fruit",
    406	: "Redwood log",
    407	: "Magical log",
    408	: "Potion of swiftiness",
    409	: "Potion of negotiation",
    410	: "Potion of resurrection",
    411	: "Potion of forgery",
    412	: "Potion of great sight",
    413	: "Potion of trickery",
    414	: "Potion of dark magic",
    415	: "Potion of pure power",
    416	: "Potion of ancient knowledge",
    560	: "Tool belt",
    570	: "Warriors toolbelt",
    571	: "Archers toolbelt",
    572	: "Mages toolbelt",
    610	: "Rare compost",
    787	: "Otherworldly gemstone"
}
def get_item_id(item_name):
    _id_list = [_id for _id, _val in id_item_dict.items() if _val == item_name.capitalize()]
    if len(_id_list) == 1:
        return _id_list[0]
    else:
        print(f"Something went wrong with get_item_id(\"{item_name}\")")
        print(f"Please make sure that there is no typo in \"{item_name}\", and that it has been added to id_item_dict")
        exit()

def get_price_info(id):
    ''' If save has been loaded and price info for that id can be found from it, returns that.
        Othervise does a new API call for that id, and returns it. (this saves/updates it into the save file even if the save is not loaded) '''
    price_info = save_system.get_price_info_from_currently_loaded_price_infos(id)
    if price_info != None:
        return price_info
    else:
        url = f'https://query.idleclans.com/api/PlayerMarket/items/prices/latest/comprehensive/{id}'
        try:
            response = requests.get(url)

            if response.status_code == 200:
                posts = response.json()
                if id in id_item_dict: save_system.update_price_infos_in_memory(posts)
                return posts
            elif response.status_code == 429:
                print('\033[1;33mError: Too many requests to API in minute!')
                print_timer_line("lets wait ", 60, "seconds, and try again.")
                return get_price_info(id)
            else:
                print('\033[1;33mError:', response.status_code)
        except requests.exceptions.RequestException as e:
            print('\033[1;33mError:', e)
            return None

def get_profit_per_hour(materials_price, product_price, sec_per_product, active_boost, change_to_save_materials=10):
    products_per_hour = 3600/sec_per_product * (100+active_boost)/100
    _materials_price = materials_price * (100-change_to_save_materials)/100
    profit_per_product = product_price - _materials_price
    return round(profit_per_product * products_per_hour)

def get_price_with_good_quantity(price_info, x_PricesWithVolume, required_amount_in_gold = 50000):
    price_counter = 0
    amount_counter = 0
    for listing in price_info[x_PricesWithVolume]:
        _amount = int(listing['key'])
        _price  = int(listing['value'])
        if price_counter + (_amount * _price) < required_amount_in_gold:
            price_counter += round(_price) * _amount
            amount_counter += round(_price)
        elif (price_counter == 0):
            price_counter += _price * _amount
            amount_counter += round(_price)
            break
        else:
            amount = round((required_amount_in_gold - price_counter) / _amount)
            price_counter += amount * _amount
            amount_counter += amount
            break
    average_price = round(price_counter / amount_counter, 1)
    #print(f"\033[1;90m{average_price}g / {item_type}(average {x_PricesWithVolume} for {amount_counter} best listings)\033[1;37m")
    return average_price

def ask_if(question):
	print('\007')#beep sound
	while True:
		answer = input(question + "\033[96m y/n: \033[0m")
		if answer == "y":
			return True
		elif answer == "n":
			return False

def print_timer_line(lineStart, retry_timer, line_end):
    print()
    while retry_timer > 0:
        time.sleep(0.1)
        retry_timer -= 0.1
        if retry_timer < 0: retry_timer=0
        print(f"\033[A{lineStart}{round(retry_timer, 1)}{line_end}")