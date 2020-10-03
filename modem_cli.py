from modem import Modem
import time

modem = Modem()
inp=1
while 1 :
    # get keyboard input
    inp = input()
    if inp == 'exit':
        modem.close()
        exit()
    else:
        modem.send_AT_command(inp)
        print(modem.get_response())
        print(modem.get_response())
        print(modem.get_response())