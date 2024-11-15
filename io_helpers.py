import time

def ask_if(question):
	print('\007')#beep sound
	while True:
		answer = input(question + "\033[96m y/n: \033[0m")
		if answer == "y":
			return True
		elif answer == "n":
			return False

def print_timer_line(lineStart, retry_timer, line_end, exit_if_interrupted=None):
    while retry_timer > 0:
        if exit_if_interrupted != None: exit_if_interrupted()
        time.sleep(0.1)
        retry_timer -= 0.1
        if retry_timer < 0: retry_timer=0
        print(f"\033[1;37m{lineStart}{round(retry_timer, 1)}{line_end}  ", end="\r", flush=True)

def prepare_profit_variables_for_printing(variables_list):
    '''this will apply ":," to the numberic values, and avoids problems when some value happens to be strings instead '''
    str_variables = []
    for variable in variables_list:
        str_variable = str(variable)  if  (not str(variable).lstrip("-").isdigit())  else  f"{int(variable):,}"
        str_variables.append(str_variable.removesuffix(".0"))
    return str_variables

def adjust_parts_of_lines(fragmented_lines_list, separator=" | "):
    fragment_len_list = []
    for fragmented_line in fragmented_lines_list:
        for i in range(len(fragmented_line)):
            if (len(fragment_len_list) < i+1):
                fragment_len_list.append(len(fragmented_line[i]))
            elif fragment_len_list[i] < len(fragmented_line[i]):
                fragment_len_list[i] = len(fragmented_line[i])
    
    result_lines_list = []
    adjusted_fragment_lines_list = [[] for _ in fragmented_lines_list]
    line_counter = 0
    for fragmented_line in fragmented_lines_list:
        for i in range(len(fragmented_line)):
            adjusted_fragment_lines_list[line_counter].append(fragmented_line[i].ljust(fragment_len_list[i]))
        result_lines_list.append(separator.join(adjusted_fragment_lines_list[line_counter]))
        line_counter += 1

    return result_lines_list
