import requests
import helpers
from helpers import ask_if, get_price_info

# put information of a sell offer of some item here, and the script will notify about it if it is found from some item IDs queried price informations. And this way you can try and find out a id of some specific item quite easily.
to_search_dict = {              # price         amount
    #"Raw superior meat" :      {'key': 640, 'value': 1748.0},
    #"Onion" :                  {'key': 166, 'value': 3708.0},
    #"Nettle" :                 {'key': 149, 'value': 611230.0}#,
    #"Watermelon" :             {'key': 500, 'value': 2756011.0}

}

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
for id_range in not_used_id_ranges:
     not_used_id_list += range(id_range[0], id_range[1]+1)

known_id_item_pairs_dict = helpers.id_item_dict

def main(start_id = 0, amount_to_check = 3):
    already_found_id_list = list(known_id_item_pairs_dict.keys())
    end_id = start_id + amount_to_check
    skip_id_count = 0
    for current_id in range(start_id, end_id):
        cur_id = current_id + skip_id_count
        _skipped = False
        first_of_already_found_id = -1
        first_of_not_used_id = -1
        while (cur_id in already_found_id_list) or (cur_id in not_used_id_list):
            if cur_id in already_found_id_list:
                #print(f"\n\033[1;34m{known_id_item_pairs_dict[cur_id]} (ID {cur_id}) already found", end = "")
                if first_of_already_found_id == -1:
                    first_of_not_used_id = -1
                    first_of_already_found_id = cur_id
                    print(f"\n\033[1;34mID {cur_id} already found ({known_id_item_pairs_dict[cur_id]})", end = "")
                else:
                    print(f"\n\033[F\033[1;34mIDs {first_of_already_found_id}-{cur_id} already found (" + "|".join([known_id_item_pairs_dict[i] for i in range(first_of_already_found_id, cur_id+1)]) + ")", end = "")
            else:
                if first_of_not_used_id == -1:
                    first_of_already_found_id = -1
                    first_of_not_used_id = cur_id
                    print(f"\n\033[1;90mID {cur_id} not used", end = "")
                else:
                    print(f"\n\033[F\033[1;90mIDs {first_of_not_used_id}-{cur_id} not used", end = "")
            skip_id_count += 1
            cur_id = current_id + skip_id_count
            _skipped = True
        if _skipped:
            print()

        price_info = get_price_info(cur_id)

        print("\033[1;37m\n" + str(cur_id))
        for search_item in to_search_dict:
            if to_search_dict[search_item] in price_info['lowestSellPricesWithVolume']:
                print("\033[1;32mFOUND: "+search_item)
                break

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

    if ask_if(f"query {amount_to_check} next IDs starting from ID {cur_id+1} ?"):
            main(cur_id+1, amount_to_check)

if __name__ == '__main__':
    main()