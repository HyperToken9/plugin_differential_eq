import textwrap


# pretty printing massive
def indent(text, amount=4, ch=' '):
    return textwrap.indent(text, amount * ch)


class Potential:
    def __init__(self, voltage=0):
        self.volts = voltage

    def __str__(self):
        return str(self.volts)

    def __sub__(self, other):
        return self.volts - other.volts


class Node:
    # A node connects to A Singular Terminal of an Element
    # And can connect to multiple other nodes
    def __init__(self, parent_element, voltage=0, links=None):
        # Voltage level at the node
        self.V = Potential(voltage)

        # Current Flowing Into Element
        self.I = 0

        self.parent = parent_element

        self.nodes = links
        if links is None:
            self.nodes = []

    def add(self, node):
        if node not in self.nodes:
            self.nodes.append(node)

    def propagate_potential(self):
        for node in self.nodes:
            node.V = self.V

    def propagate_current(self):
        for node in self.nodes:
            node.parent.set_currents()

    def get_current(self):
        return self.I

    def set_current(self, i):
        self.I = i

    def get_voltage(self):
        return self.V.volts

    def set_voltage(self, v):
        self.V.volts = v

    def __str__(self):
        # return f"ID: {hex(id(self))}\nVoltage: {self.V}\nLinks To: {[i.parent for i in self.nodes]}\n"
        return f"Voltage: {self.V}\nCurrent: {self.I}\nLinks To: {[i.parent for i in self.nodes]}\n"

class CircuitElement:
    def __init__(self, voltage_a=0, voltage_b=0):
        self.A = Node(self, voltage_a)
        self.B = Node(self, voltage_b)

    def connect(self, other):
        for parent_node in [self.B] + self.B.nodes:
            for child_node in [other.A] + other.A.nodes:
                parent_node.add(child_node)
                child_node.add(parent_node)

    def get_voltage(self):
        return self.B.V - self.A.V

    def simulate(self):
        print("Beginning Simulation")
        self.A.propagate_potential()

        self.A.propagate_current()

    def set_currents(self):
        return

    def drop_voltage(self):
        return

    def __str__(self):
        return "Node A:\n" + indent(self.A.__str__()) + "Node B:\n" + indent(self.B.__str__())
        # return indent(self.A.__str__())

    def __repr__(self):
        return "Circuit_Element"


class IdealResistor(CircuitElement):
    def __init__(self, resistance):
        super().__init__()
        self.R = resistance

    def set_currents(self):
        mag_i = self.get_voltage()/ self.R
        self.A.set_current(mag_i)
        self.B.set_current(-1 * mag_i)
        self.drop_voltage()

    def drop_voltage(self):
        # print("Voltage Drop: ", self.A.get_current() * self.R)
        self.A.set_voltage(self.B.get_voltage() - self.A.get_current() * self.R)

    def __str__(self):
        return f"Resistance: {self.R}\nID: {hex(id(self))}\n" + super().__str__()

    def __repr__(self):
        return f"R({self.R})"


class IdealDCVoltage(CircuitElement):

    def __init__(self, voltage):
        super().__init__(voltage)
        self.V = voltage

    def __str__(self):
        return f"Voltage: {self.V}\nID: {hex(id(self))}\n" + super().__str__()

    def __repr__(self):
        return f"V({self.V})"


def main():
    v1 = IdealDCVoltage(100)
    r1 = IdealResistor(10)
    r2 = IdealResistor(20)
    r3 = IdealResistor(30)

    v1.connect(r1)
    r1.connect(r2)
    r2.connect(r3)
    r3.connect(v1)

    v1.simulate()

    print(v1)
    print(r1)
    print(r2)
    print(r3)

    # print(f"{r3.get_current()}")


if "__main__" == __name__:
    main()
