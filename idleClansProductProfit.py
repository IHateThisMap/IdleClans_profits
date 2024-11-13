import sys
from helpers import get_item_id, get_price_info, get_profit_per_hour, get_price_with_good_quantity
from save_system import load_price_infos_from_save, load_arguments_from_save, save_arguments_to_file
sys.path.append('../py_script_launcher_UI/')
from UI import run_command_handler

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

def _handle_price_validity(price, price_type, item_name):
    if price == -1:
        _buy_or_sell = "buy" if price_type=="highestBuyPricesWithVolume" else "sell"
        print(f"\033[1;37mThere is 0 {_buy_or_sell} offers for {item_name}.\033[1;90m You may be able to do good deals with {_buy_or_sell}ing this item right now!!\033[1;37m")
        return False
    return True


def get_prices_and_profits(cur_product, material_price_type, product_price_type, active_boost, change_to_save_materials):
    total_material_price = 0
    for material in products_dict[cur_product][0]:
        material_price_info = get_price_info(get_item_id(material[1]))
        selling_material_price = get_price_with_good_quantity(material_price_info, material_price_type)
        if _handle_price_validity(selling_material_price, material_price_type, material[1]):
            if total_material_price != -1:
                total_material_price += selling_material_price * material[0]
        else:
            total_material_price = -1

    product_price_info = get_price_info(get_item_id(cur_product))
    product_price = get_price_with_good_quantity(product_price_info, product_price_type)
    _product_price_valid = _handle_price_validity(product_price, product_price_type, cur_product)

    if _product_price_valid and total_material_price != -1:
        profit_per_hour = get_profit_per_hour(total_material_price, product_price, products_dict[cur_product][1], active_boost, change_to_save_materials)
        return profit_per_hour, product_price, total_material_price
    elif _product_price_valid:
        return "???", product_price, "???"
    elif total_material_price != -1:
        return "???", "???", total_material_price
    else:
        raise Exception("the code should never go here. So this is a bug")


def main(cur_product, active_boost=0, change_to_save_materials=0):
    print(f"\n..................{cur_product.upper()}..................")

    min_profit_per_hour, buying_product_price, total_selling_material_price = get_prices_and_profits(cur_product, 'lowestSellPricesWithVolume', 'highestBuyPricesWithVolume', active_boost, change_to_save_materials)
    print(f"\033[1;90m(min_profit_per_hour \033[1;37m{min_profit_per_hour}\033[1;90m for instant buying and selling prices) ({buying_product_price}g/product) ({total_selling_material_price}/materials)\033[1;37m")

    max_profit_per_hour, selling_product_price, total_buying_material_price = get_prices_and_profits(cur_product, 'highestBuyPricesWithVolume', 'lowestSellPricesWithVolume', active_boost, change_to_save_materials)
    print(f"\033[1;90m(max_profit_per_hour \033[1;32m{max_profit_per_hour}\033[1;90m for slow buying and selling listings) ({selling_product_price}g/product) ({total_buying_material_price}/materials)\033[1;37m")

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
    print(f"product: \"{product}\", active_boost: \"{active_boost}\", change_to_save_materials: \"{change_to_save_materials}\", use_API: \"{use_API}\"")

    save_arguments_to_file(activity_name="PotionsAndBars", argument_list_to_save=(product, active_boost, change_to_save_materials, use_API))

    use_API_bool = use_API == "use API"
    if not use_API_bool:
        load_price_infos_from_save()

    if product == "all":
        for cur_fruit in products_dict:
            main(cur_fruit, active_boost, change_to_save_materials)
    else:
        main(product, active_boost, change_to_save_materials)