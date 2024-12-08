import signal_handling
import sys
from io_helpers import adjust_parts_of_lines, prepare_profit_variables_for_printing, color
from helpers import get_item_id, get_price_info, calculate_products_per_hour, calculate_profit_per_hour, calculate_price_with_good_quantity
from save_system import load_price_infos_from_save, load_arguments_from_save, save_arguments_to_file
sys.path.append('../py_script_launcher_UI/')
from UI import run_command_handler # type: ignore

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

def _get_fruit_profits_line_parts_str_list(starting_text, fruit_price, seed_price, fruits_per_hour, show_extra_info=True):
    if show_extra_info:
        fruit_price_str, five_fruits_price_str, seed_price_str, fruits_per_hour_str = prepare_profit_variables_for_printing((fruit_price, fruit_price*5, seed_price, fruits_per_hour))
        five_fruits_price_str, fruits_per_hour_str = five_fruits_price_str + " g/5fruits", fruits_per_hour_str + " fruit/h"
    else:
        fruit_price_str, seed_price_str = prepare_profit_variables_for_printing((fruit_price, seed_price))
        five_fruits_price_str, fruits_per_hour_str = "", ""

    return (starting_text, f"{fruit_price_str} g/fruit", five_fruits_price_str, f"{seed_price_str} g/seed", fruits_per_hour_str)

def _get_price_info(id, retry_time=60):
    return get_price_info(id, retry_time=retry_time, exit_if_interrupted=signal_handling.exit_if_interrupted)

def _get_line_parts_for_average_prices(pre_price_description_str, seed_price, fruit_price, farmings_per_hour, price_color="default", post_price_description_str="", show_extra_info=True):
    """
    Prepares and returns a line that is separated in parts.

   :param pre_price_description_str: string that is printed before the price
   :type pre_price_description_str: str
   :param seed_price: the price of the seed
   :type seed_price: int
   :param fruit_price: the price of the fruit
   :type fruit_price: int
   :param farmings_per_hour: how many seeds are grown into fruits in an hour
   :type farmings_per_hour: int
   :param post_price_description_str: (optional) string that is printed after the price
   :type post_price_description_str: str
   :param show_extra_info: if False then will put empty strings to the places less important strings
   :type show_extra_info: bool
   :return: tuple that contains strings that shall be aligned and printed onto 1 line later with other similar lines
   :rtype: tuple
    """
    avg_profit_per_hour = calculate_profit_per_hour(seed_price, fruit_price*5, farmings_per_hour, change_to_save_materials)
    return _get_fruit_profits_line_parts_str_list(f"\033[1;90m{pre_price_description_str}{color(price_color)}{avg_profit_per_hour:,}\033[1;90m g/h{post_price_description_str}",
                             fruit_price, seed_price, fruits_per_hour=farmings_per_hour*5, show_extra_info=show_extra_info)

def main(cur_fruit, active_boost, change_to_save_materials):
    print(f"..................{cur_fruit.upper()}..................".ljust(140, "."))
    fruit_price_info = _get_price_info(get_item_id(cur_fruit))
    seed_price_info =  _get_price_info(get_item_id(cur_fruit + " seed"))
    farmings_per_hour = calculate_products_per_hour(fruits_dict[cur_fruit], active_boost)


    selling_seed_price = calculate_price_with_good_quantity(seed_price_info, 'lowestSellPricesWithVolume')
    buying_fruit_price = calculate_price_with_good_quantity(fruit_price_info, 'highestBuyPricesWithVolume')
    line1_parts = _get_line_parts_for_average_prices("MIN estimated profit ", selling_seed_price, buying_fruit_price, farmings_per_hour, "default", " (instantly buying and selling)")

    line2_parts = _get_line_parts_for_average_prices("Last 1 Days average prices profit  ", seed_price_info['averagePrice1Day'], fruit_price_info['averagePrice1Day'], farmings_per_hour, "yellow", show_extra_info=False)
    line3_parts = _get_line_parts_for_average_prices("Last 7 Days average prices profit  ", seed_price_info['averagePrice7Days'], fruit_price_info['averagePrice7Days'], farmings_per_hour, "yellow", show_extra_info=False)
    line4_parts = _get_line_parts_for_average_prices("Last 30 Days average prices profit ", seed_price_info['averagePrice30Days'], fruit_price_info['averagePrice30Days'], farmings_per_hour, "yellow", show_extra_info=False)

    buying_seed_price = calculate_price_with_good_quantity(seed_price_info, 'highestBuyPricesWithVolume', 10000)
    selling_fruit_price = calculate_price_with_good_quantity(fruit_price_info, 'lowestSellPricesWithVolume', 10000)
    line5_parts = _get_line_parts_for_average_prices("MAX estimated profit ", buying_seed_price, selling_fruit_price, farmings_per_hour, "green", " (slowly buying and selling)")

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
    if len(sys.argv)==2 and sys.argv[1] == "ui":
        print(f"\033[1;90myou can run this again without UI by replasing \"ui\" in the comand you used with:\033[1;37m \"{product}\" \"{active_boost}\" \"{change_to_save_materials}\" \"{use_API}\"")
        print("\033[1;90myou are also always able to run the script with the previously used settings by using no arguments at all\033[1;37m")
    elif len(sys.argv)==1:
        print(f"\033[1;90myou can run this again also with using these arguments:\033[1;37m \"{product}\" \"{active_boost}\" \"{change_to_save_materials}\" \"{use_API}\"")

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