import requests
from io_helpers import print_timer_line
import save_system

_id_item_dict = {
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
    87	: "Titanium platebody",
    88	: "Titanium platelegs",
    89	: "Titanium helmet",
    90	: "Titanium shield",
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
    236	: "Titanium boots",
    243	: "Titanium gloves",
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
    _id_list = [_id for _id, _val in _id_item_dict.items() if _val == item_name.capitalize()]
    if len(_id_list) == 1:
        return _id_list[0]
    else:
        print(f"Something went wrong with get_item_id(\"{item_name}\")")
        print(f"Please make sure that there is no typo in \"{item_name}\", and that it has been added to _id_item_dict")
        exit()

def get_item_name(item_id):
    if is_id_known(item_id):
        return _id_item_dict[item_id]
    else:
        print("Error! Tried to get name for non existing id: " + str(item_id))
        exit()

def is_id_known(id):
    return (id in list(_id_item_dict.keys()))

def get_price_info(id, retry_time, exit_if_interrupted = None):
    ''' If save has been loaded and price info for that id can be found from it, returns that.
        Othervise does a new API call for that id, and returns it. (this saves/updates it into the save file even if the save is not loaded) '''
    price_info = save_system.get_price_info_from_currently_loaded_price_infos(id)
    if price_info != None:
        return price_info
    else:
        #Might be better to not do any more API calls if interruption is signaled
        #if exit_if_interrupted != None: exit_if_interrupted()

        url = f'https://query.idleclans.com/api/PlayerMarket/items/prices/latest/comprehensive/{id}'
        try:
            response = requests.get(url)

            if response.status_code == 200:
                posts = response.json()
                if id in _id_item_dict:
                    if _check_offers_from_price_info(_id_item_dict[id], posts):
                        save_system.update_price_info_in_save_file(posts)
                    else:
                        print(f"\033[1;90m(skipped saving price info of {_id_item_dict[id]} to save file)\033[1;37m")
                        save_system.update_price_info_only_in_current_session(posts)
                return posts
            elif response.status_code == 429:
                print('\n\033[1;33mError: Too many requests to API in a minute! (the limit is 40)')
                print_timer_line("lets wait ", retry_time, "seconds, and try again.", exit_if_interrupted)
                if retry_time > 10:
                    retry_time = 10
                return get_price_info(id, retry_time, exit_if_interrupted)
            else:
                print('\033[1;33mError:', response.status_code)
        except requests.exceptions.RequestException as e:
            print('\033[1;33mError:', e)
            return None

def _check_offers_from_price_info(item_name, price_info, price_types=('lowestSellPricesWithVolume', 'highestBuyPricesWithVolume')):
    found_types_of_orders = []
    for price_type in price_types:
        if len(price_info[price_type]) == 0:
            _buy_or_sell = "buy" if ("Buy" in price_type) else "sell"
            print(f"\033[1;37mThere is 0 {_buy_or_sell} offers for {item_name}.\033[1;33m You may be able to do good deals with {_buy_or_sell}ing this item right now!!\033[1;37m")
            found_types_of_orders.append(False)
        found_types_of_orders.append(True)
    return False not in found_types_of_orders

def calculate_profit_per_hour(materials_price, product_price, sec_per_product, active_boost, change_to_save_materials):
    if materials_price == -1 and product_price == -1:
        return "???"
    products_per_hour = 3600/sec_per_product * (100+active_boost)/100
    if materials_price == -1:
         return f"(({product_price}-materials_price)*{round(products_per_hour)})"
    _materials_price = materials_price * (100-change_to_save_materials)/100
    if product_price == -1:
         return f"((product_price-{round(_materials_price)})*{round(products_per_hour)})"
    profit_per_product = product_price - _materials_price
    return round(profit_per_product * products_per_hour)

def calculate_price_with_good_quantity(price_info, x_PricesWithVolume, required_amount_in_gold = 50000):
    price_counter = 0
    amount_counter = 0
    if len(price_info[x_PricesWithVolume]) == 0:
        return -1
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
