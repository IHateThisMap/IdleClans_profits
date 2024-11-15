import signal_handling
import sys
from io_helpers import adjust_parts_of_lines
from helpers import get_item_id, get_price_info, calculate_profit_per_hour, calculate_price_with_good_quantity
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

def get_fruit_profits_line_parts_str_list(starting_text, fruit_price, seed_price, show_5_fruits_price=True, fill_char = " "):
    five_fruits_price_str = f"{round(fruit_price*5):,} g/5_fruits"
    if not show_5_fruits_price: 
        five_fruits_price_str = "".ljust(len(five_fruits_price_str), fill_char)
    return(starting_text, f"{round(fruit_price):,} g/fruit", five_fruits_price_str, f"{round(seed_price):,} g/seed")

def _get_price_info(id, retry_time=60):
    return get_price_info(id, retry_time=retry_time, exit_if_interrupted=signal_handling.exit_if_interrupted)

def main(cur_fruit, active_boost, change_to_save_materials):
    print(f"..................{cur_fruit.upper()}..................".ljust(140, "."))
    fruit_price_info = _get_price_info(get_item_id(cur_fruit))
    seed_price_info =  _get_price_info(get_item_id(cur_fruit + " seed"))


    selling_seed_price = calculate_price_with_good_quantity(seed_price_info, 'lowestSellPricesWithVolume')
    buying_fruit_price = calculate_price_with_good_quantity(fruit_price_info, 'highestBuyPricesWithVolume')
    min_profit_per_hour = calculate_profit_per_hour(selling_seed_price, buying_fruit_price*5, fruits_dict[cur_fruit], active_boost, change_to_save_materials)
    line1_parts = get_fruit_profits_line_parts_str_list(f"\033[1;90mMIN estimated profit \033[1;37m{min_profit_per_hour:,}\033[1;90m g/h for instantly buying seeds and instantly selling fruits",
                             buying_fruit_price, selling_seed_price)


    avg_profit_per_hour_1Day = calculate_profit_per_hour(seed_price_info['averagePrice1Day'], fruit_price_info['averagePrice1Day']*5, fruits_dict[cur_fruit], active_boost, change_to_save_materials)
    line2_parts = get_fruit_profits_line_parts_str_list(f"\033[1;90mLast 1 Days average prices profit  \033[1;33m{avg_profit_per_hour_1Day:,}\033[1;90m g/h",
                             fruit_price_info['averagePrice1Day'], seed_price_info['averagePrice1Day'], show_5_fruits_price=False)
    
    avg_profit_per_hour_7Days = calculate_profit_per_hour(seed_price_info['averagePrice7Days'], fruit_price_info['averagePrice7Days']*5, fruits_dict[cur_fruit], active_boost, change_to_save_materials)
    line3_parts = get_fruit_profits_line_parts_str_list(f"\033[1;90mLast 7 Days average prices profit  \033[1;33m{avg_profit_per_hour_7Days:,}\033[1;90m g/h",
                             fruit_price_info['averagePrice7Days'], seed_price_info['averagePrice7Days'], show_5_fruits_price=False)

    avg_profit_per_hour_30Days = calculate_profit_per_hour(seed_price_info['averagePrice30Days'], fruit_price_info['averagePrice30Days']*5, fruits_dict[cur_fruit], active_boost, change_to_save_materials)
    line4_parts = get_fruit_profits_line_parts_str_list(f"\033[1;90mLast 30 Days average prices profit \033[1;33m{avg_profit_per_hour_30Days:,}\033[1;90m g/h",
                             fruit_price_info['averagePrice30Days'], seed_price_info['averagePrice30Days'], show_5_fruits_price=False)


    buying_seed_price = calculate_price_with_good_quantity(seed_price_info, 'highestBuyPricesWithVolume', 10000)
    selling_fruit_price = calculate_price_with_good_quantity(fruit_price_info, 'lowestSellPricesWithVolume', 10000)
    max_profit_per_hour = calculate_profit_per_hour(buying_seed_price, selling_fruit_price*5, fruits_dict[cur_fruit], active_boost, change_to_save_materials)
    line5_parts = get_fruit_profits_line_parts_str_list(f"\033[1;90mMAX estimated profit \033[1;32m{max_profit_per_hour:,}\033[1;90m for slowly buying seeds and selling fruits throughg listings",
                             selling_fruit_price, buying_seed_price)

    lines = adjust_parts_of_lines((line1_parts, line2_parts, line3_parts, line4_parts, line5_parts))
    for l in lines:
        print(l)

fruits_list = ["all"] + list(fruits_dict.keys())
argument_options = (("Farm ", fruits_list), 
                    ("with ", range(0, 50), f"% active boost"), 
                    ("and with ", [10 * i for i in range(0, 6)], f"% chance to save the seeds"), 
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
        signal_handling.setup_sigint_handler("")
        for cur_fruit in fruits_dict:
            signal_handling.exit_if_interrupted()
            main(cur_fruit, active_boost, change_to_save_materials)
    else:
        main(product, active_boost, change_to_save_materials)