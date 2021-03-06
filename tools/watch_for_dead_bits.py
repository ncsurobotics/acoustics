from __future__ import division

import time
import functools

from bbb import boot


def match_against(comp, *args):
    """ Useful for processing user command line input
    """
    return comp in args


class Mask:

    """
    """

    def __init__(self):
        self.burn_bit = 1
        self.capture = [0] * 12
        self.word_size = 12

    # Consider replacing both of these functions with a single function
    # that has a burn=True keyword argument.  That way, there's no
    # duplication of the same code - dralley

    def burn(self, samples, delay):
        format_code = '0' + str(self.word_size) + 'b'
        T = delay / float(len(samples))

        # Grab a sample
        for sample in samples:

            # Convert it to binary
            b_sample = format(sample, format_code)

            # Burn in those values
            for i in range(self.word_size):
                # Count down w/ index
                index = self.word_size - 1 - i

                # Inspect each bit for burn-in
                #import pdb; pdb.set_trace()
                if b_sample[index] == str(self.burn_bit):
                    self.capture[index] = self.burn_bit

            # Wait certain amount of time for next loop
            print(''.join(map(str, self.capture)))
            time.sleep(T)

    def normal(self, samples, delay):
        format_code = '0' + str(self.word_size) + 'b'
        T = delay / float(len(samples))

        # Grab a sample
        for sample in samples:

            # Convert it to binary
            b_sample = format(sample, format_code)

            # Wait certain amount of time for next loop
            print(b_sample)
            time.sleep(T)


def main(adc):
    # config the ADC for success
    adc.config([0x100])
    adc.ready_pruss_for_burst()

    # config burning maching
    msk = Mask()

    #
    print("normal or burn?")
    user_input = raw_input(" >> ")

    # Creates a function that will return true if user_input matches
    # any of the provided variable arguments
    input_matches = functools.partial(match_against, user_input)

    # Some error handling
    if input_matches('burn'):
        print("What value should burn (1 or 0)?")
        msk.burn_bit = raw_input(" >> ")

    elif user_input != 'normal':
        print("I don't recognize that. Quitting program.")
        user_input = 'q'

    while user_input != 'q':
        try:
            # Capture Data
            y, _ = adc.burst(raw=1)

            # Parse The Data
            if user_input == 'burn':
                msk.burn(y[0], .1)

            elif user_input == 'normal':
                msk.normal(y[0], .1)

            # Uncomment to allow for user loop control
            # user_input = raw_input('Press enter to continue...')
        except KeyboardInterrupt:
            print("Quitting program")
            break

    boot.dearm()
