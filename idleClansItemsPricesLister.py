import signal_handling
from io_helpers import ask_if, print_timer_line
from helpers import get_price_info, is_id_known, get_item_name
import sys

# put information of a sell offer of some item here, and the script will notify about it if it is found from some item IDs queried price informations. And this way you can try and find out a id of some specific item quite easily.
to_search_dict = {              # price         amount
    #"Titanium boots" :          {'key': 78999, 'value': 5.0},
    #"Titanium gloves" :         {'key': 100000, 'value': 8.0}
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

def _get_price_info(id, retry_time=60):
    return get_price_info(id, retry_time=retry_time, exit_if_interrupted=signal_handling.exit_if_interrupted)

def main(start_id, amount_to_check):
    skip_id_count = 0
    api_call_count = 0
    starting_id_checking = True
    while api_call_count < amount_to_check:
        signal_handling.exit_if_interrupted()
        cur_id = start_id + api_call_count + skip_id_count

        while(True):
            first_of_already_found_id = -1
            while is_id_known(cur_id):
                if first_of_already_found_id == -1:
                    first_of_already_found_id = cur_id
                    print(f"\n\033[1;34mID {cur_id} already found ({get_item_name(cur_id)})\033[1;37m", end = "")
                else:
                    print(f"\n\033[F\033[1;34mIDs {first_of_already_found_id}-{cur_id} already found (" + "|".join([get_item_name(i) for i in range(first_of_already_found_id, cur_id+1)]) + ")", end = "")
                skip_id_count += 1
                cur_id = start_id + api_call_count + skip_id_count

            first_of_not_used_id = -1
            while (cur_id in not_used_id_list):
                if first_of_not_used_id == -1:
                    first_of_not_used_id = cur_id
                    print(f"\n\033[1;90mID {cur_id} not used", end = "")
                else:
                    print(f"\n\033[F\033[1;90mIDs {first_of_not_used_id}-{cur_id} not used", end = "")
                skip_id_count += 1
                cur_id = start_id + api_call_count + skip_id_count
            
            _some_api_calls_skipped_now = (first_of_already_found_id != -1) or (first_of_not_used_id != -1)
            if not _some_api_calls_skipped_now:
                break
            else:
                starting_id_checking = True

        if starting_id_checking:
            before_checked_id_print = "\n\033[1;37mChecking IDs: "
        else:
            before_checked_id_print = "\033[1;90m,\033[1;37m "

        api_call_count += 1
        price_info = _get_price_info(cur_id)

        for search_item in to_search_dict:
            if to_search_dict[search_item] in price_info['lowestSellPricesWithVolume']:
                checked_id_print = f"\n\033[1;32m{cur_id} FOUND: {search_item}\033[1;90m (manually check that it is not a false-positive, and add to helpers.py -> _id_item_dict):\n " + str(price_info)
                starting_id_checking = True
                break
        else:
            checked_id_print = "\033[1;37m" + str(cur_id)
            starting_id_checking = False

        print(before_checked_id_print + checked_id_print, flush=True, end="")

    print()

    if ask_if(f"query {amount_to_check} next IDs starting from ID {cur_id+1} ?"):
        main(cur_id+1, amount_to_check)

    #print_timer_line("lets wait ", 120, "seconds, and check the next " + str(amount_to_check) + " IDs", signal_handling.exit_if_interrupted)
    #main(cur_id+1, amount_to_check)


if __name__ == '__main__':
    signal_handling.setup_sigint_handler()
    argument = int(sys.argv[1])  if  len(sys.argv)>1 and (sys.argv[1].isdigit())  else  0
    main(argument, 40)