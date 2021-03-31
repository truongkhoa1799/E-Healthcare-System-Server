import time

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def LogMesssage(msg, opt = 1):
    if opt == 0:
        # Header
        print(bcolors.HEADER + "[{time}]: {msg}".format(time=time.strftime("%H:%M:%S",time.localtime()), msg=msg))
    elif opt == 1:
        # message
        print(bcolors.OKCYAN + "[{time}]: {msg}".format(time=time.strftime("%H:%M:%S",time.localtime()), msg=msg))
    else:
        print(bcolors.FAIL + "[{time}]: {msg}".format(time=time.strftime("%H:%M:%S",time.localtime()), msg=msg))
