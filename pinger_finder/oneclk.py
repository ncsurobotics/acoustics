from sys import argv

from acoustics import Acoustics
import locate_pinger
import quickplot


def main(cmd=None):
    if (cmd is None):
        cmd = argv[1]

    if (cmd == 'competition'):
        # Load ADC Stuff
        acoustics = Acoustics()
        acoustics.preset(0)
        val = locate_pinger.main(acoustics.adc, dearm=False)  # degrees right

        # Dearm ADC outside of locate_pinger.py.
        acoustics.adc.unready()

        # return value to the user
        return val

    elif (cmd == 'competition-cont'):
        # Load ADC Stuff
        acoustics = Acoustics()
        acoustics.preset(0)

        # Locate pinger
        while True:
            # Exits on CTRL-C
            try:
                locate_pinger.main(acoustics.adc, dearm=False)
            except KeyboardInterrupt:
                print("Quitting program")
                break

        # Dearm ADC outside of locate_pinger.py.
        acoustics.adc.unready()

    elif (cmd == 'plt'):
        # Load plotting stuff
        plt = load_matplotlib()

        # Load ADC Stuff
        acoustics = Acoustics()
        acoustics.preset(100)
        acoustics.adc.adc_status()
        quickplot.main(acoustics.adc, plt)


def load_matplotlib():
    print("Loading Matplotlib library...")
    import matplotlib

    matplotlib.use('GTK')

    import matplotlib.pyplot as plt

    plt.ioff()
    plt.hold(False)
    plt.close()
    print("...done.")

    return plt

if __name__ == '__main__':
    main()
