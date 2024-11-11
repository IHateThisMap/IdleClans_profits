import time
import requests

# put information of a sell offer of some item here, and the script will notify about it if it is found from some item IDs queried price informations. And this way you can try and find out a id of some specific item quite easily.
to_search_dict = {              # price         amount
    #"Raw superior meat" :      {'key': 640, 'value': 1748.0},
    #"Onion" :                  {'key': 166, 'value': 3708.0},
    #"Nettle" :                 {'key': 149, 'value': 611230.0}#,
    #"Watermelon" :             {'key': 500, 'value': 2756011.0}

}

#IDs range from 0 to ?800?
#already_found_id_list = [0, 1, 2, 6, 7, 8, 9, 10, 
#                         15, 31, 42, 46, 54, 
#                         113, 
#                         118, 
#                         122,
#                         125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 
#                         155, 156, 157, 158, 159, 160, 161, 162, 
#                         225, 226, 227, 228, 229, 230, 
#                         248, 
#                         265, 266, 273, 274, 275, 
#                         337, 378, 
#                         399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416,
#                         560, 570, 571, 572,
#                         610,
#                         787]

# These had no price history at all, so I assumed they are just not used. But there could be some very rarely sold/bought items.
not_used_id_ranges = [(267,272), 
                      (338,346), (394,398), 
                      (417,428), (452,532), 
                      (573,579), (588,599), 
                      (630,641), (669,671), (679,682), (685,691), 
                      (702,739), (745,764), (766,786), (788,790), 
                      (845,908)]
not_used_id_list = [3, 
                    5, 
                    11, 
                    16, 17, 18, 19, 
                    40, 
                    44, 
                    99, 
                    101, 
                    103, 
                    107, 108, 109, 
                    119, 120, 121, 
                    123, 124, 
                    139, 
                    142, 
                    147, 
                    166, 167, 
                    336,
                    381, 382, 383,
                    551,
                    661, 663, 665,
                    794, 795, 
                    807, 
                    809, 810, 811, 
                    815, 816, 817, 
                    836, 837
                    ]

known_id_item_pairs_dict = {
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
    400	: "grape seed",
    401	: "grape",
    402	: "Papaya seed",
    403	: "Papaya",
    404	: "Dragon fruit seed",
    405	: "Dragon fruit",
    406	: "Redwood log",
    407	: "Magical log",
    408	: "Potion of swiftness",
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



for id_range in not_used_id_ranges:
     not_used_id_list += range(id_range[0], id_range[1]+1)

def get_price_info(id):
    url = f'https://query.idleclans.com/api/PlayerMarket/items/prices/latest/comprehensive/{id}'

    try:
        response = requests.get(url)

        if response.status_code == 200:
            posts = response.json()
            return posts
        else:
            print('Error:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None

def _ask_if(question):
	print('\007')#beep sound
	while True:
		answer = input(question + "\033[96m y/n: \033[0m")
		if answer == "y":
			return True
		elif answer == "n":
			return False
          
def _print_timer_line(lineStart, retry_timer, line_end):
    print()
    while retry_timer > 0:
        time.sleep(0.1)
        retry_timer -= 0.1
        if retry_timer < 0: retry_timer=0
        print(f"\033[A{lineStart}{round(retry_timer, 1)}{line_end}")

def main(start_id = 395):
    already_found_id_list = list(known_id_item_pairs_dict.keys())
    end_id = start_id + 30
    skip_id_count = 0
    for loop_count in range(start_id, end_id):
        cur_id = loop_count + skip_id_count
        _skipped = False
        first_of_already_found_id = -1
        first_of_not_used_id = -1
        while (cur_id in already_found_id_list) or (cur_id in not_used_id_list):
            if cur_id in already_found_id_list:
                #print("\033[1;34mID: " + str(cur_id) + "\033[1;90m(already found)")
                #print(f"\n\033[1;34m{known_id_item_pairs_dict[cur_id]} (ID {cur_id}) already found", end = "")
                if first_of_already_found_id == -1:
                    first_of_not_used_id = -1
                    first_of_already_found_id = cur_id
                    print(f"\n\033[1;34mID {cur_id} already found ({known_id_item_pairs_dict[cur_id]})", end = "")
                else:
                    print(f"\n\033[F\033[1;34mIDs {first_of_already_found_id}-{cur_id} already found (" + "|".join([known_id_item_pairs_dict[i] for i in range(first_of_already_found_id, cur_id+1)]) + ")", end = "")

            else:
                #print(f"\n\033[1;90mID {cur_id} not used", end = "")
                if first_of_not_used_id == -1:
                    first_of_already_found_id = -1
                    first_of_not_used_id = cur_id
                    print(f"\n\033[1;90mID {cur_id} not used", end = "")
                else:
                    print(f"\n\033[F\033[1;90mIDs {first_of_not_used_id}-{cur_id} not used", end = "")
            skip_id_count += 1
            cur_id = loop_count + skip_id_count
            _skipped = True
        if _skipped:
            print()

        price_info = get_price_info(cur_id)

        print("\033[1;37m\n" + str(cur_id))
        for search_item in to_search_dict:
            #print("\033[1;90m ", end = "")
            #print("search_item: "+search_item)
            #print("to_search_dict[search_item]: " + str(to_search_dict[search_item]))
            if to_search_dict[search_item] in price_info['lowestSellPricesWithVolume']:
                print("\033[1;32mFOUND: "+search_item)
                #print("\033[1;32m ", end = "")
                break
            #else:
            #    print("\033[1;37m", end = "")


        if price_info:
            print('lowestSellPricesWithVolume:', price_info['lowestSellPricesWithVolume'])
            print('highestBuyPricesWithVolume:', price_info['highestBuyPricesWithVolume'])
            print('averagePrice1Day:', price_info['averagePrice1Day'])
        
            if price_info['averagePrice7Days'] > 10000000:
                print("\033[1;91m", end = "")
            print('averagePrice7Days:', price_info['averagePrice7Days'])
            print("\033[1;37m", end = "")

            print('averagePrice30Days:', price_info['averagePrice30Days'])

            if price_info['tradeVolume1Day'] > 500000:
                print("\033[1;91m", end = "")
            print('tradeVolume1Day:', price_info['tradeVolume1Day'])
            print("\033[1;37m", end = "")
        else:
            print('Failed to fetch posts from API.')

    _print_timer_line("can do queries again in ", 60, "seconds")
    if _ask_if(f"query 30 next IDs starting from ID {cur_id+1} ?"):
            main(cur_id+1)

if __name__ == '__main__':
    main()