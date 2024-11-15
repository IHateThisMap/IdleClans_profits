### add signal_handling.setup_sigint_handler() at before           the loop that the program runs in
#   and signal_handling.exit_if_interrupted()  at the start/end of the loop that the program runs in
import signal

interrupt = False
sigint_message = ""

def _signal_handler(sig, frame):
    global interrupt
    if sigint_message != "":
        print(f'\n\033[1;33m{sigint_message}\033[1;37m')
    interrupt = True

def exit_if_interrupted():
    '''Call this from somewhere inside of the loop that the program runs in'''
    if interrupt:
        import sys
        sys.exit("\n\033[1;33mINTERRUPTED\033[1;37m")

def is_interrupted():
    return interrupt

def setup_sigint_handler(_sigint_message="You pressed Ctrl+C! The program should stop soon."):
    global sigint_message
    sigint_message = _sigint_message

    signal.signal(signal.SIGINT, _signal_handler)
    print("\033[1;34mSIGINT handler enabled. You can press CTRL + C to grafecully end the program\033[1;37m")
