### add signal_handling.check_if_interrupted() at the end or start of the loop that the program 
import signal

interrupt = False

def _signal_handler(sig, frame):
    global interrupt
    print('\n\033[1;33mYou pressed Ctrl+C! The probram should stop soon.\033[1;37m')
    interrupt = True

def exit_if_interrupted():
    '''Call this from somewhere inside of the loop that the program runs in'''
    if interrupt:
        import sys
        sys.exit("\n\033[1;33mINTERRUPTED\033[1;37m")

signal.signal(signal.SIGINT, _signal_handler)
print("INTSIG handler enabled. You can press CTRL + C to grafecully end the program")
