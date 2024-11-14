import pickle
import os

SAVE_FOLDER = "save_folder/"
price_infos_in_memory_dict = {}

def update_price_info_only_in_current_session(posts):
    '''will not touch to the save files at all, but only makes the script remember this price info until it has finished running'''
    global price_infos_in_memory_dict
    id = posts["itemId"]
    price_infos_in_memory_dict[id] = posts

def update_price_info_in_save_file(posts):
    ''' will not overwrite the possibly existing save file, just adds to it or updates element in it '''
    global price_infos_in_memory_dict
    save_file_name = "icPriceInfo.dictionary"
    id = posts["itemId"]
    price_infos_in_memory_dict[id] = posts

    # price_infos_in_memory_dict can be less complete than the save file, so here we do not want to override the save with it, but instead only update this one IDs price info value
    loaded_dict = _load_from_save(save_file_name, {})
    loaded_dict[id] = price_infos_in_memory_dict[id]
    with open(SAVE_FOLDER + save_file_name, 'wb') as save_file:
        pickle.dump(price_infos_in_memory_dict, save_file)

def _load_from_save(save_file_name, default_return_value):
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)
    if os.path.isfile("./" + SAVE_FOLDER + save_file_name):
        with open(SAVE_FOLDER + save_file_name, 'rb') as save_file:
            loaded_dict = pickle.load(save_file)
        return loaded_dict
    return default_return_value

def load_price_infos_from_save():
    global price_infos_in_memory_dict
    price_infos_in_memory_dict = _load_from_save('icPriceInfo.dictionary', {})

def get_price_info_from_currently_loaded_price_infos(id):
    global price_infos_in_memory_dict
    if id in price_infos_in_memory_dict:
        #print("found price info from loaded save data for item ID: " + str(id))
        return price_infos_in_memory_dict[id]
    else:
        #print("did not find price info from loaded save data for item ID: " + str(id))
        return None

def load_arguments_from_save(activity_name, default_return = ()):
    save_file_name = f'ic{activity_name.capitalize()}Arguments.list'
    return _load_from_save(save_file_name, default_return)

def save_arguments_to_file(activity_name, argument_list_to_save):
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)
    save_file_name = f'ic{activity_name.capitalize()}Arguments.list'
    with open(SAVE_FOLDER + save_file_name, 'wb') as save_file:
        pickle.dump(argument_list_to_save, save_file)