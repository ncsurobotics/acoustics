from . import gpio


class Port():

    """ Each instance of Port represents a group of pins on the beaglebone.
    This group of pins is actually a group of GPIO instances. The Caller
    may specify this group during instantiation, or afterwards with the
    (self).createPort(...) method.
    """

    def __init__(self, assignment=None):
        """
        Args:
            assignment (optional): in case the caller would like to define the port during
        instantiation. See: the pinNameList argument of the createPort() method
        """

        self.en = True
        self.pins = []
        self.direction = []
        self.portDirection = ''
        self.value = []
        self.nValue = 0
        self.length = 0
        if assignment:
            self.createPort(assignment)

    def createPort(self, pinNameList):
        """ Assigns a port, which is just a group of pins.

        Args:
            pinNameList: Represents a list of strings specifying BBB pins from
                the end user's POV. The format of this specification is "Px_y",
                whereas x is the header number on the BBB, y is the pin number
                on that particular header (including leading zeros). Thus,
                strings such as "P8_01", "P8_46", "P9_02" are valid.

                pinNameList[0] must represent the LSB,
                pinNameList[-1] must represent the MSB
        """

        # If user supplies a string (which is convenient if he
        # only wants to allocate one pin), then convert that string
        # to a list with one element because that's the type that
        # works with self.batchLookupGPIO(...)
        if isinstance(pinNameList, basestring):
            pinNameList = [pinNameList]

        GPIOList = gpio.batch_lookup(pinNameList)

        for pin in GPIOList:
            # print(pinNameList) ; print(GPIOList)

            obj_pin = gpio.GPIO(pin)
            self.pins.append(obj_pin)  # self.pins
            self.direction.append(obj_pin.direction)  # self.direction
            self.value.append(obj_pin.value)  # self.value

        self.length = len(self.pins)  # self.length

    def readStr(self):
        """ Reads values of all pins that make up a port (self) and returns a
        binary string with the MSB on the left and the LSB on the right
        """

        s = ""
        i = 0
        for pin in self.pins:
            a = pin.read()
            s = str(a) + s
            self.value[i] = a
        return s

    def writeToPort(self, value):
        """ Takes the integer 'value' and converts it to a
        string formated in binary representation, which is parsed in
        the for loop in order to configure each pin on the port.
        """

        portLength = len(self.pins)
        binaryVal = ('{0:0' + str(portLength) + 'b}').format(value)  # generate binary string from value arg

        for i in range(portLength):
            s_i = (portLength - 1) - i
            b = int(binaryVal[s_i])
            self.pins[i].write(b)

    def setPortDir(self, direction):
        """ Sets all pins on a port to a direction and updates
        self.portDirection and self.direction accordingly.

        Args:
            direction: String "in" or "out", to update
        """

        i = 0
        for pin in self.pins:
            pin.set_direction(direction)
            self.direction[i] = pin.direction
            i += 1

        self.portDirection = direction

    def close(self):
        """ Closes every pin on a port. See: close() method on GPIO
        """

        for pin in self.pins:
            pin.close()

    def help(self):
        """ Prints a list of all available attributes and methods
        """

        print("You can call the following attributes: ")
        for item in self.__dict__.keys():
            print("  *.{}".format(item))

        print()
        print("You also have access to the following methods: ")
        for item in [method for method in dir(self) if callable(getattr(self, method))]:
            print("  *.{}()".format(item))
        print()