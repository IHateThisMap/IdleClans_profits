import sys
from helpers import get_item_id, get_price_info
from save_system import load_save
sys.path.append('../py_script_launcher_UI/')
from UI import run_command_handler

fruits_dict = {         # fruits_per_hour (base time)
    "potato" :           880,
    "carrot" :           660,
    "tomato" :           440,
    "cabbage" :          440,
    "strawberry" :       290,
    "watermelon" :       220,
    "grape" :            175,
    "papaya" :           160,
    "dragon fruit" :     145
}

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
    fruit_price_info = get_price_info(get_item_id(cur_fruit))
    seed_price_info =  get_price_info(get_item_id(cur_fruit + " seed"))


    selling_seed_price = get_price_with_good_quantity(seed_price_info, 'lowestSellPricesWithVolume', "SEED")
    buying_fruit_price = get_price_with_good_quantity(fruit_price_info, 'highestBuyPricesWithVolume', "FRUIT")
    min_profit_per_hour = get_profit_per_hour(selling_seed_price, buying_fruit_price, fruits_dict[cur_fruit], active_boost, change_to_save_materials)
    print(f"\033[1;90m(min_profit_per_hour \033[1;37m{min_profit_per_hour:,}\033[1;90m for instant buying and selling prices) ({buying_fruit_price}g/fruit) ({selling_seed_price}/seed)")

    avg_profit_per_hour_1Day = get_profit_per_hour(seed_price_info['averagePrice1Day'], fruit_price_info['averagePrice1Day'], fruits_dict[cur_fruit], active_boost, change_to_save_materials)
    print(f"\033[1;90m(avg_profit_per_hour_1Day   \033[1;33m{avg_profit_per_hour_1Day:,}\033[1;90m)")
    avg_profit_per_hour_7Days = get_profit_per_hour(seed_price_info['averagePrice7Days'], fruit_price_info['averagePrice7Days'], fruits_dict[cur_fruit], active_boost, change_to_save_materials)
    print(f"\033[1;90m(avg_profit_per_hour_7Days  \033[1;33m{avg_profit_per_hour_7Days:,}\033[1;90m)")
    avg_profit_per_hour_30Days = get_profit_per_hour(seed_price_info['averagePrice30Days'], fruit_price_info['averagePrice30Days'], fruits_dict[cur_fruit], active_boost, change_to_save_materials)
    print(f"\033[1;90m(avg_profit_per_hour_30Days \033[1;33m{avg_profit_per_hour_30Days:,}\033[1;90m)")

    #buying_seed_price = seed_price_info['highestBuyPricesWithVolume'][0]['key']
    #selling_fruit_price = fruit_price_info['lowestSellPricesWithVolume'][0]['key']
    buying_seed_price = get_price_with_good_quantity(seed_price_info, 'highestBuyPricesWithVolume', "SEED", 10000)
    selling_fruit_price = get_price_with_good_quantity(fruit_price_info, 'lowestSellPricesWithVolume', "FRUIT", 10000)
    max_profit_per_hour = get_profit_per_hour(buying_seed_price, selling_fruit_price, fruits_dict[cur_fruit], active_boost, change_to_save_materials)
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
        load_save()

    if product == "all":
        for cur_fruit in fruits_dict:
            main(cur_fruit, active_boost, change_to_save_materials)
    else:
        main(product, active_boost, change_to_save_materials)