import sys
import requests
sys.path.append('../py_script_launcher_UI/')
from UI import run_command_handler

SAVE_FOLDER = "save_folder/"
SAVE_FILE = SAVE_FOLDER + 'icSavedPriceInfo.dictionary'

fruits_dict = {     #(seed_id, fruit_id, fruits_per_hour)
    "potato" :           (126, 132, 880),
    "carrot" :           (127, 133, 660),
    "tomato" :           (128, 134, 440),
    "cabbage" :          (129, 135, 440),
    "strawberry" :       (130, 136, 290),
    "watermelon" :       (131, 137, 220),
    "grape" :            (400, 401, 175),
    "papaya" :           (402, 403, 160),
    "dragon fruit" :     (404, 405, 145)
}

def _print_timer_line(lineStart, retry_timer, line_end):
    print()
    while retry_timer > 0:
        import time
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

def get_profit_per_hour(seed_price, fruit_price, fruits_per_hour, active_boost, change_to_save_materials):
    _seed_price = seed_price * (100-change_to_save_materials)/100
    profit_per_fruit = fruit_price - round(_seed_price/5)
    return profit_per_fruit * fruits_per_hour * (100+active_boost)/100

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
   # print(f"\033[1;90m{item_type}(average {x_PricesWithVolume} for {amount_counter} best listings is {average_price})\033[1;37m")
    return average_price

def main(cur_fruit, active_boost, change_to_save_materials):
    print(f"..................{cur_fruit.upper()}..................")
    seed_price_info = get_price_info(fruits_dict[cur_fruit][0])
    fruit_price_info = get_price_info(fruits_dict[cur_fruit][1])


    selling_seed_price = get_price_with_good_quantity(seed_price_info, 'lowestSellPricesWithVolume', "SEED")
    buying_fruit_price = get_price_with_good_quantity(fruit_price_info, 'highestBuyPricesWithVolume', "FRUIT")
    min_profit_per_hour = get_profit_per_hour(selling_seed_price, buying_fruit_price, fruits_dict[cur_fruit][2], active_boost, change_to_save_materials)
    print(f"\033[1;90m(min_profit_per_hour \033[1;37m{min_profit_per_hour:,}\033[1;90m for instant buying and selling prices) ({buying_fruit_price}g/fruit) ({selling_seed_price}/seed)")

    avg_profit_per_hour_1Day = get_profit_per_hour(seed_price_info['averagePrice1Day'], fruit_price_info['averagePrice1Day'], fruits_dict[cur_fruit][2], active_boost, change_to_save_materials)
    print(f"\033[1;90m(avg_profit_per_hour_1Day   \033[1;33m{avg_profit_per_hour_1Day:,}\033[1;90m)")
    avg_profit_per_hour_7Days = get_profit_per_hour(seed_price_info['averagePrice7Days'], fruit_price_info['averagePrice7Days'], fruits_dict[cur_fruit][2], active_boost, change_to_save_materials)
    print(f"\033[1;90m(avg_profit_per_hour_7Days  \033[1;33m{avg_profit_per_hour_7Days:,}\033[1;90m)")
    avg_profit_per_hour_30Days = get_profit_per_hour(seed_price_info['averagePrice30Days'], fruit_price_info['averagePrice30Days'], fruits_dict[cur_fruit][2], active_boost, change_to_save_materials)
    print(f"\033[1;90m(avg_profit_per_hour_30Days \033[1;33m{avg_profit_per_hour_30Days:,}\033[1;90m)")

    #buying_seed_price = seed_price_info['highestBuyPricesWithVolume'][0]['key']
    #selling_fruit_price = fruit_price_info['lowestSellPricesWithVolume'][0]['key']
    buying_seed_price = get_price_with_good_quantity(seed_price_info, 'highestBuyPricesWithVolume', "SEED", 10000)
    selling_fruit_price = get_price_with_good_quantity(fruit_price_info, 'lowestSellPricesWithVolume', "FRUIT", 10000)
    max_profit_per_hour = get_profit_per_hour(buying_seed_price, selling_fruit_price, fruits_dict[cur_fruit][2], active_boost, change_to_save_materials)
    print(f"\033[1;90m(max_profit_per_hour \033[1;32m{max_profit_per_hour:,}\033[1;90m for slow buying and selling listings) ({selling_fruit_price}g/fruit) ({buying_seed_price}/seed)")

fruits_list = ["all"] + list(fruits_dict.keys())
argument_options = (("Farm ", fruits_list), 
                    ("with ", range(0, 50), f"% active boost"), 
                    ("and with ", [10 * i for i in range(0, 5)], f"% chance to save the seeds"), 
                    ("and ", ["use previously queried and saved prices", "use API"]))
        
if __name__ == '__main__':
    product, active_boost, change_to_save_materials, use_API = run_command_handler(argument_options, sys.argv)
    #product, active_boost, change_to_save_materials, use_API = "potato", 32, 20, "use API"

    use_API_bool = use_API == "use API"
    if not use_API_bool:
        price_infos_in_memory_dict = load_price_infos_from_save()

    if product == "all":
        for cur_fruit in fruits_dict:
            main(cur_fruit, active_boost, change_to_save_materials)
    else:
        main(product, active_boost, change_to_save_materials)