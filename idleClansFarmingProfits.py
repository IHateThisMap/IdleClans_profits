import sys
from helpers import get_item_id, get_price_info, get_profit_per_hour, get_price_with_good_quantity
from save_system import load_price_infos_from_save, load_arguments_from_save, save_arguments_to_file
sys.path.append('../py_script_launcher_UI/')
from UI import run_command_handler

fruits_dict = {         # sec_per_5_fruits
    "Potato" :           30,
    "Carrot" :           40,
    "Tomato" :           60,
    "Cabbage" :          60,
    "Strawberry" :       90,
    "Watermelon" :       120,
    "Grape" :            150,
    "Papaya" :           165,
    "Dragon fruit" :     180
}

def main(cur_fruit, active_boost, change_to_save_materials):
    print(f"..................{cur_fruit.upper()}..................")
    fruit_price_info = get_price_info(get_item_id(cur_fruit))
    seed_price_info =  get_price_info(get_item_id(cur_fruit + " seed"))


    selling_seed_price = get_price_with_good_quantity(seed_price_info, 'lowestSellPricesWithVolume')
    buying_fruit_price = get_price_with_good_quantity(fruit_price_info, 'highestBuyPricesWithVolume')
    min_profit_per_hour = get_profit_per_hour(selling_seed_price, buying_fruit_price*5, fruits_dict[cur_fruit], active_boost, change_to_save_materials)
    print(f"\033[1;90m(min_profit_per_hour \033[1;37m{min_profit_per_hour:,}\033[1;90m for instant buying and selling prices) ({buying_fruit_price}g/fruit) ({buying_fruit_price*5}g/5fruits) ({selling_seed_price}/seed)")

    avg_profit_per_hour_1Day = get_profit_per_hour(seed_price_info['averagePrice1Day'], fruit_price_info['averagePrice1Day']*5, fruits_dict[cur_fruit], active_boost, change_to_save_materials)
    print(f"\033[1;90m(avg_profit_per_hour_1Day   \033[1;33m{avg_profit_per_hour_1Day:,}\033[1;90m)")
    avg_profit_per_hour_7Days = get_profit_per_hour(seed_price_info['averagePrice7Days'], fruit_price_info['averagePrice7Days']*5, fruits_dict[cur_fruit], active_boost, change_to_save_materials)
    print(f"\033[1;90m(avg_profit_per_hour_7Days  \033[1;33m{avg_profit_per_hour_7Days:,}\033[1;90m)")
    avg_profit_per_hour_30Days = get_profit_per_hour(seed_price_info['averagePrice30Days'], fruit_price_info['averagePrice30Days']*5, fruits_dict[cur_fruit], active_boost, change_to_save_materials)
    print(f"\033[1;90m(avg_profit_per_hour_30Days \033[1;33m{avg_profit_per_hour_30Days:,}\033[1;90m)")

    #buying_seed_price = seed_price_info['highestBuyPricesWithVolume'][0]['key']
    #selling_fruit_price = fruit_price_info['lowestSellPricesWithVolume'][0]['key']
    buying_seed_price = get_price_with_good_quantity(seed_price_info, 'highestBuyPricesWithVolume', 10000)
    selling_fruit_price = get_price_with_good_quantity(fruit_price_info, 'lowestSellPricesWithVolume', 10000)
    max_profit_per_hour = get_profit_per_hour(buying_seed_price, selling_fruit_price*5, fruits_dict[cur_fruit], active_boost, change_to_save_materials)
    print(f"\033[1;90m(max_profit_per_hour \033[1;32m{max_profit_per_hour:,}\033[1;90m for slow buying and selling listings) ({selling_fruit_price}g/fruit) ({selling_fruit_price*5}g/5fruits) ({buying_seed_price}/seed)")

fruits_list = ["all"] + list(fruits_dict.keys())
argument_options = (("Farm ", fruits_list), 
                    ("with ", range(0, 50), f"% active boost"), 
                    ("and with ", [10 * i for i in range(0, 5)], f"% chance to save the seeds"), 
                    ("and ", ["use API", "use previously queried and saved prices"]))
        
if __name__ == '__main__':
    _default_values = load_arguments_from_save(activity_name="Farming")#, default_return=("Cabbage", 32, 30, "use API"))

    product, active_boost, change_to_save_materials, use_API = run_command_handler(argument_options, _default_values)
    #product, active_boost, change_to_save_materials, use_API = "potato", 32, 20, "use API"
    print(f"product: \"{product}\", active_boost: \"{active_boost}\", change_to_save_materials: \"{change_to_save_materials}\", use_API: \"{use_API}\"")

    save_arguments_to_file(activity_name="Farming", argument_list_to_save=(product, active_boost, change_to_save_materials, use_API))

    use_API_bool = use_API == "use API"
    if not use_API_bool:
        load_price_infos_from_save()

    if product == "all":
        for cur_fruit in fruits_dict:
            main(cur_fruit, active_boost, change_to_save_materials)
    else:
        main(product, active_boost, change_to_save_materials)