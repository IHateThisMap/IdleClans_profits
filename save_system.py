SAVE_FOLDER = "save_folder/"
SAVE_FILE = SAVE_FOLDER + 'icSavedPriceInfo.dictionary'
price_infos_in_memory_dict = {}

def update_price_infos_in_memory(posts):
    ''' will not overwrite the possibly existing save file, just adds to it or updates element in it '''
    global price_infos_in_memory_dict
    id = posts["itemId"]
    price_infos_in_memory_dict[id] = posts

    # price_infos_in_memory_dict can be less complete than the save file, so here we do not want to override the save with it, but instead only update this one IDs price info value
    loaded_dict = _load_price_infos_from_save()
    loaded_dict[id] = price_infos_in_memory_dict[id]
    import pickle
    with open(SAVE_FILE, 'wb') as save_file:
        pickle.dump(price_infos_in_memory_dict, save_file)

def _load_price_infos_from_save():
    ''''''
    import os
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)
    if os.path.isfile("./" + SAVE_FILE):
        import pickle
        with open(SAVE_FILE, 'rb') as save_file:
            loaded_dict = pickle.load(save_file)
        return loaded_dict
    return {}

def load_save():
    global price_infos_in_memory_dict
    price_infos_in_memory_dict = _load_price_infos_from_save()

def get_price_info_from_currently_loaded_price_infos(id):
    global price_infos_in_memory_dict
    if id in price_infos_in_memory_dict:
        #print("found price info from loaded save data for item ID: " + str(id))
        return price_infos_in_memory_dict[id]
    else:
        #print("did not find price info from loaded save data for item ID: " + str(id))
        return None