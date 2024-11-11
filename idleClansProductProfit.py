import time
import requests
import sys
sys.path.append('../py_script_launcher_UI/')
from UI import run_command_handler

SAVE_FOLDER = "save_folder/"
SAVE_FILE = SAVE_FOLDER + 'icSavedPriceInfo.dictionary'

coal_ore_id = 31
titanium_ore_id = 42
titanium_bar_id = 46

products_dict = {         #     materials                                                               product_ID       sec_per_product              products_per_hour
    "titanium bar" :           (((9, 31, "coal ore"), (3, 42, "titanium ore")),                                 46,           30),            #141),
    "Potion of swiftiness" :   (((10, 134, "tomato"), (5, 118, "Nettle"), (2, 1, "Pine log")),                  408,          55),            #69.6),
    "Potion of resurrection" : (((15, 135, "cabbage"), (10, 274, "Enchanted flax"), (2, 2, "Chestnut log")),    410,          72.5),            #52.8),
    "Potion of great sight" :  (((10, 137, "watermelon"), (15, 273, "Magical flax"), (2, 8, "Teak log")),       412,          97.5),            #39.3),
    "Potion of trickery" :     (((10, 401, "grapes"), (15, 125, "Porcini"), (2, 10, "Yew log")),                413,          115),            #33.3),
    "Potion of dark magic" :   (((10, 403, "papaya"), (15, 275, "cursed flax"), (2, 406, "Redwood log")),       414,          132.5),            #27),
    "Potion of pure power" :   (((15, 403, "papaya"), (20, 399, "Seaweed"), (2, 407, "Magical log")),           415,          155),            #23)
}

def _print_timer_line(lineStart, retry_timer, line_end):
    print()
    while retry_timer > 0:
        time.sleep(0.1)
        retry_timer -= 0.1
        if retry_timer < 0: retry_timer=0
        print(f"\033[A{lineStart}{round(retry_timer, 1)}{line_end}")

price_infos_in_memory_dict = {}

def update_price_infos_in_memory(posts, price_infos_in_memory_dict):
    id = posts["itemId"]
    price_infos_in_memory_dict[id] = posts

    # price_infos_in_memory_dict can be less complete than the save file, so here we do not want to override the save with it, bitinstead only update this one IDs price info value
    loaded_dict = load_price_infos_from_save()
    loaded_dict[id] = price_infos_in_memory_dict[id]
    import pickle
    with open(SAVE_FILE, 'wb') as save_file:
        pickle.dump(price_infos_in_memory_dict, save_file)
    return price_infos_in_memory_dict

def load_price_infos_from_save():
    import os
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)
    if os.path.isfile("./" + SAVE_FILE):
        import pickle
        with open(SAVE_FILE, 'rb') as save_file:
            loaded_dict = pickle.load(save_file)
        return loaded_dict
    return {}

def get_price_info(id):
    if id in price_infos_in_memory_dict:
        #print("skipped API call " + str(id))
        return price_infos_in_memory_dict[id]
    else:
        #print("starting API call " + str(id))
        url = f'https://query.idleclans.com/api/PlayerMarket/items/prices/latest/comprehensive/{id}'
        try:
            response = requests.get(url)

            if response.status_code == 200:
                posts = response.json()
                update_price_infos_in_memory(posts, price_infos_in_memory_dict)
                return posts
            elif response.status_code == 429:
                print('\033[1;33mError: Too many requests to API in minute!')
                _print_timer_line("lets wait ", 60, "seconds, and try again.")
                return get_price_info(id)
            else:
                print('\033[1;33mError:', response.status_code)
        except requests.exceptions.RequestException as e:
            print('\033[1;33mError:', e)
            return None

def get_profit_per_hour(materials_price, product_price, sec_per_product, active_boost, change_to_save_materials=10):
    products_per_hour = 3600/sec_per_product * (100+active_boost)/100
    _materials_price = materials_price * (100-change_to_save_materials)/100
    profit_per_bar = product_price - round(_materials_price)
    return profit_per_bar * products_per_hour

def get_price_with_good_quantity(price_info, x_PricesWithVolume, item_type, required_amount_in_gold = 50000):
    i = 0
    price_counter = 0
    amount_counter = 0
    for listing in price_info[x_PricesWithVolume]:
        if price_counter + (listing['value'] * listing['key']) < required_amount_in_gold:
            price_counter += round(listing['value']) * listing['key']
            amount_counter += round(listing['value'])
        elif (price_counter == 0):
            price_counter += listing['value'] * listing['key']
            amount_counter += round(listing['value'])
            break
        else:
            amount = round((required_amount_in_gold - price_counter) / listing['key'])
            price_counter += amount * listing['key']
            amount_counter += amount
            break
    average_price = round(price_counter / amount_counter, 1)
    #print(f"\033[1;90m{average_price}g / {item_type}(average {x_PricesWithVolume} for {amount_counter} best listings)\033[1;37m")
    return average_price

def get_prices_and_profits(cur_product, material_price_type, product_price_type, active_boost, change_to_save_materials):
    total_material_price = 0
    for material in products_dict[cur_product][0]:
        material_price_info = get_price_info(material[1])
        selling_material_price = get_price_with_good_quantity(material_price_info, material_price_type, material[2])
        total_material_price += selling_material_price * material[0]

    product_price_info = get_price_info(products_dict[cur_product][1])
    product_price = get_price_with_good_quantity(product_price_info, product_price_type, cur_product.upper())

    profit_per_hour = get_profit_per_hour(total_material_price, product_price, products_dict[cur_product][2], active_boost, change_to_save_materials)

    return profit_per_hour, product_price, total_material_price


def main(cur_product, active_boost=0, change_to_save_materials=0):
    print(f"\n..................{cur_product.upper()}..................")

    min_profit_per_hour, buying_product_price, total_selling_material_price = get_prices_and_profits(cur_product, 'lowestSellPricesWithVolume', 'highestBuyPricesWithVolume', active_boost, change_to_save_materials)
    print(f"\033[1;90m(min_profit_per_hour \033[1;37m{min_profit_per_hour:,}\033[1;90m for instant buying and selling prices) ({buying_product_price}g/product) ({total_selling_material_price}/materials)")

    max_profit_per_hour, selling_product_price, total_buying_material_price = get_prices_and_profits(cur_product, 'highestBuyPricesWithVolume', 'lowestSellPricesWithVolume', active_boost, change_to_save_materials)
    print(f"\033[1;90m(max_profit_per_hour \033[1;32m{max_profit_per_hour:,}\033[1;90m for slow buying and selling listings) ({selling_product_price}g/product) ({total_buying_material_price}/materials)")

products_list = ["all"] + list(products_dict.keys())
#products_list = ["all", "potions", "metals", "farming"] + list(products_dict.keys())
print(str(products_list))
argument_options = (("Produce ", products_list), 
                    ("with ", range(0, 50), f"% active boost"), 
                    ("and with ", [10 * i for i in range(0, 5)], f"% chance to save the materials"), 
                    ("and ", ["use previously queried and saved prices", "use API"]))

if __name__ == '__main__':
    product, active_boost, change_to_save_materials, use_API = run_command_handler(argument_options, sys.argv)
    #product, active_boost, change_to_save_materials, use_API = "titanium bar", 32, 20, "use API"

    use_API_bool = use_API == "use API"
    if not use_API_bool:
        price_infos_in_memory_dict = load_price_infos_from_save()

    if product == "all":
        for cur_fruit in products_dict:
            main(cur_fruit, active_boost, change_to_save_materials)
    else:
        main(product, active_boost, change_to_save_materials)