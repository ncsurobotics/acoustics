from os import path

# Get variables for navigating the file system.
root_directory = path.dirname(path.dirname(path.realpath(__file__)))
hc_directory = path.join(root_directory, "host_communication")
pf_directory = path.join(root_directory, "pinger_finder")

# Add important directories to path
import sys
sys.path.insert(0, hc_directory)
sys.path.insert(0, pf_directory)

import serial as s
import signal
import uart #enable_uart()
import oneclk
from acoustics import Acoustics
from acoustics import Logging

# ######################
### Global Constants ###
#########################

def define_commlink():
    uart.enable_uart()
    print("Opening Port %s." % PORT_NAME)
    return s.Serial(PORT_NAME, 9600, timeout=1)


PORT_NAME = "/dev/ttyO5"
acoustics = Acoustics() # Acoustics Control Object
pAC = define_commlink() # Acoustics communication port
log = Logging()
INTERRUPT_WINDOW = 1 # seconds

# ######################
### Other definitions ##
#######################
    
def init_acoustics():
    acoustics.preset(0)

def init_interrupt_timer():
    def raw_input_timeout_hdl(signum, frame):
        # This error is meant to be caught and suppressed in a try statement
        raise IOError("This isn't really an error.")
        
    # The backend activation of SIGALRM will invoke the 
    # raw_input_timeout_hdl function
    signal.signal(signal.SIGALRM, raw_input_timeout_hdl)
    
def send(msg):
    pAC.write(msg + '\n')

def read():
    input =  pAC.readline()
    if input:
        if (input[-1] != '\n'):
            print("String is missing \\n terminator!")
        
        return input.rstrip('\n')
    
    return None
    
def usage(port):
    pass
    
def process_input(port):
    input = port.readline()
    if input:
        # Show input as a means of debugging output
        print("Acoustics: RX'd %r." % input)
        
        # Other logic for input
        if (input == "locate pinger"):
            # Recieve cmd from seawolf requesting location of pinger
            val = oneclk.main('competition')
            if val==None:
                print("Unable to get data")
                pAC.write('None\n')
            else:
                print(val)
                pAC.write(str(val)+'\n')
            
        elif (input =="help"):
            usage(pAC)
            
        else:
            print("Acoustics: RX'd %r, an unrecognized cmd!!!" % input)
            usage(pAC)


def task_manager(input):
    if input=="locate pinger":
        angle_to_pinger = acoustics.compute_pinger_direction()
        send( str(angle_to_pinger) )
        
    elif input=="hello":
        send("Hello to you too, Seawolf.")
    else:
        send("Unknown command! Please enter 'locate pinger' or 'hello'.")
        

def main_loop():

    while 1:
        dummy = ''
        try:
            # Try reading and acting upon seawolf's input first
            input = read()
            if input:
                print("RX: {0}".format(input))
                task_manager(input)
            else:
                print("I got nothin.")
                
            # Now see if someone is trying to do something on the backend
            signal.setitimer(signal.ITIMER_REAL, INTERRUPT_WINDOW)
            dummy = raw_input()
            signal.setitimer(signal.ITIMER_REAL, 0)
            
            # Enter debug mode if backend user asks to
            if dummy == 'g':
                print("Acoustics debug mode activated.")
                print("Please enter one of the following commands:")
                list_of_cmds = ("l: log latest recorded data.\n"
                    + "g: Change gain of input filters.\n"
                    + "c: continue terminal program.\n"
                    + "p: Plot last sample collection.\n"
                    + "test_config: Load the acoustic test config\n"
                    + "q: Quit this app.\n")
                print(list_of_cmds)
                int_input = raw_input(">> ")
                if (int_input=='q'):
                    print("Closing Port %s." % PORT_NAME)
                    pAC.close()
                    acoustics.close()
                    break
                elif (int_input=='l'):
                    log.logit(acoustics)
                elif (int_input=='g'):
                    acoustics.filt.gain_mode()
                elif (int_input=='p'):
                    acoustics.plot_recent()
                elif (int_input=='c'):
                    pass
                elif (int_input=="test_config"):
                    acoustics.preset(101)
                else:
                    pass
      
        except IOError:
            pass
            
        except KeyboardInterrupt:
            print("Closing Port %s." % PORT_NAME)
            pAC.close()
            acoustics.close()
            break
            
                
            
            

def main():
    # Initialize Components
    init_acoustics()
    init_interrupt_timer()

    # Listen for texts and process them
    print("Acoustics: UART(5) echo-terminal active. "
    + "Currently listening for any data that comes in from the FT232RL")
    
    # Run the main loop
    main_loop()

if __name__ == '__main__':
    main()