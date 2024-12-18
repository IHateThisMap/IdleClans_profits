import signal_handling
import sys
from io_helpers import prepare_profit_variables_for_printing, adjust_parts_of_lines
from helpers import get_item_id, get_price_info, calculate_products_per_hour, calculate_profit_per_hour, calculate_price_with_good_quantity
from save_system import load_price_infos_from_save, load_arguments_from_save, save_arguments_to_file
sys.path.append('../py_script_launcher_UI/')
from UI import run_command_handler # type: ignore

SAVE_FOLDER = "save_folder/"
SAVE_FILE = SAVE_FOLDER + 'icSavedPriceInfo.dictionary'

products_dict = {         #      (amount, material)                                                  sec_per_product
    "Titanium bar" :           ( ((9,  "coal ore"  ), (3,  "titanium ore"  )                     ),      30    ),
    "Potion of swiftiness" :   ( ((10, "tomato"    ), (5,  "Nettle"        ), (2, "Pine log"    )),      55    ),
    "Potion of resurrection" : ( ((15, "cabbage"   ), (10, "Enchanted flax"), (2, "Chestnut log")),      72.5  ),
    "Potion of great sight" :  ( ((10, "watermelon"), (15, "Magical flax"  ), (2, "Teak log"    )),      97.5  ),
    "Potion of trickery" :     ( ((10, "grape"     ), (15, "Porcini"       ), (2, "Yew log"     )),      115   ),
    "Potion of dark magic" :   ( ((10, "papaya"    ), (15, "cursed flax"   ), (2, "Redwood log" )),      132.5 ),
    "Potion of pure power" :   ( ((15, "papaya"    ), (20, "Seaweed"       ), (2, "Magical log" )),      155   )
}

def _get_price_info(id, retry_time=60):
    return get_price_info(id, retry_time=retry_time, exit_if_interrupted=signal_handling.exit_if_interrupted)

def get_current_prices_and_profits(cur_product, material_price_type, product_price_type, products_per_hour, change_to_save_materials):
    total_material_price = 0
    for material in products_dict[cur_product][0]:
        material_price_info = _get_price_info(get_item_id(material[1]))
        selling_material_price = calculate_price_with_good_quantity(material_price_info, material_price_type)
        if selling_material_price != -1  and  total_material_price != -1:
            total_material_price += selling_material_price * material[0]
        else:
            total_material_price = -1

    product_price_info = _get_price_info(get_item_id(cur_product))
    product_price = calculate_price_with_good_quantity(product_price_info, product_price_type, 10000)

    profit_per_hour = calculate_profit_per_hour(total_material_price, product_price, products_per_hour, change_to_save_materials)
    if product_price == -1:         product_price = "???"
    if total_material_price == -1:  total_material_price = "???"
    return prepare_profit_variables_for_printing((profit_per_hour, product_price, total_material_price))

def get_historical_average_prices_and_profits(cur_product, material_price_type, product_price_type, products_per_hour, change_to_save_materials):
    total_material_price = 0
    for material in products_dict[cur_product][0]:
        material_price_info = _get_price_info(get_item_id(material[1]))
        selling_material_price = material_price_info[material_price_type]
        if selling_material_price != -1  and  total_material_price != -1:
            total_material_price += selling_material_price * material[0]
        else:
            total_material_price = -1

    product_price_info = _get_price_info(get_item_id(cur_product))
    product_price = product_price_info[material_price_type]

    profit_per_hour = calculate_profit_per_hour(total_material_price, product_price, products_per_hour, change_to_save_materials)
    if product_price == -1:         product_price = "???"
    if total_material_price == -1:  total_material_price = "???"
    return prepare_profit_variables_for_printing((profit_per_hour, product_price, total_material_price))

def main(cur_product, active_boost=0, change_to_save_materials=0):
    print(f"\n..................{cur_product.upper()}................................................")
    lines_in_parts = []

    products_per_hour = calculate_products_per_hour(products_dict[cur_product][1], active_boost)
    min_profit_per_hour, buying_product_price, total_selling_material_price = get_current_prices_and_profits(cur_product, 'lowestSellPricesWithVolume', 'highestBuyPricesWithVolume', products_per_hour, change_to_save_materials)
    lines_in_parts.append((f"\033[1;90mMIN estimated profit \033[1;37m{min_profit_per_hour}\033[1;90m g/h (instantly buying and selling)",  f"{buying_product_price} g/product",        f"{total_selling_material_price} g/materials",  f"{round(products_per_hour, 1)} products/h\033[1;37m"))

    average_price_profit_per_hour_1Day, averag_product_price_1Day, averag_material_price_1Day = get_historical_average_prices_and_profits(cur_product, 'averagePrice1Day', 'averagePrice1Day', products_per_hour, change_to_save_materials)
    lines_in_parts.append((f"\033[1;90m1 DAY average prices profit \033[1;33m{average_price_profit_per_hour_1Day}\033[1;90m g/h",           f"{averag_product_price_1Day} g/product",   f"{averag_material_price_1Day} g/materials",    ""))

    average_price_profit_per_hour_7Days, averag_product_price_7Days, averag_material_price_7Days = get_historical_average_prices_and_profits(cur_product, 'averagePrice7Days', 'averagePrice7Days', products_per_hour, change_to_save_materials)
    lines_in_parts.append((f"\033[1;90m7 DAYs average prices profit \033[1;33m{average_price_profit_per_hour_7Days}\033[1;90m g/h",         f"{averag_product_price_7Days} g/product",  f"{averag_material_price_7Days} g/materials",   ""))

    average_price_profit_per_hour_30Days, averag_product_price_30Days, averag_material_price_30Days = get_historical_average_prices_and_profits(cur_product, 'averagePrice30Days', 'averagePrice30Days', products_per_hour, change_to_save_materials)
    lines_in_parts.append((f"\033[1;90m30 DAYs average prices profit \033[1;33m{average_price_profit_per_hour_30Days}\033[1;90m g/h",       f"{averag_product_price_30Days} g/product", f"{averag_material_price_30Days} g/materials",  ""))

    max_profit_per_hour, selling_product_price, total_buying_material_price = get_current_prices_and_profits(cur_product, 'highestBuyPricesWithVolume', 'lowestSellPricesWithVolume', products_per_hour, change_to_save_materials)
    lines_in_parts.append((f"\033[1;90mMAX estimated profit \033[1;32m{max_profit_per_hour}\033[1;90m g/h (slowly buying and selling)",     f"{selling_product_price} g/product",       f"{total_buying_material_price} g/materials",   ""))

    lines = adjust_parts_of_lines(lines_in_parts)
    for l in lines:
        print(l)


products_list = ["all"] + list(products_dict.keys())
#products_list = ["all", "potions", "metals", "farming"] + list(products_dict.keys())
print(str(products_list))
argument_options = (("Produce ",  products_list), 
                    ("with ",     range(0, 50),                  f"% active boost"), 
                    ("and with ", [10 * i for i in range(0, 5)], f"% chance to save the materials"), 
                    ("and ",      ["use API", 
                                   "use previously queried and saved prices"]))

if __name__ == '__main__':
    _default_values = load_arguments_from_save(activity_name="PotionsAndBars")#, default_return=("Potion of pure power", 32, 30, "use API"))

    product, active_boost, change_to_save_materials, use_API = run_command_handler(argument_options, _default_values)
    #product, active_boost, change_to_save_materials, use_API = "titanium bar", 32, 20, "use API"
    if len(sys.argv)==2 and sys.argv[1] == "ui":
        print(f"\033[1;90myou can run this again without UI by replasing \"ui\" in the comand you used with:\033[1;37m \"{product}\" \"{active_boost}\" \"{change_to_save_materials}\" \"{use_API}\"")
        print("\033[1;90myou are also always able to run the script with the previously used settings by using no arguments at all\033[1;37m")
    elif len(sys.argv)==1:
        print(f"\033[1;90myou can run this again also with using these arguments:\033[1;37m \"{product}\" \"{active_boost}\" \"{change_to_save_materials}\" \"{use_API}\"")

    save_arguments_to_file(activity_name="PotionsAndBars", argument_list_to_save=(product, active_boost, change_to_save_materials, use_API))

    use_API_bool = use_API == "use API"
    if not use_API_bool:
        load_price_infos_from_save()

    if product == "all":
        signal_handling.setup_sigint_handler("")
        for cur_product in products_dict:
            signal_handling.exit_if_interrupted()
            main(cur_product, active_boost, change_to_save_materials)
    else:
        main(product, active_boost, change_to_save_materials)