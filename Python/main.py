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


class Current:
    def __init__(self):
        self.amps = 0
        self.pair = None

    def set_amps(self, i):
        self.amps = i
        self.sync_pair()

    def get_amps(self):
        return self.amps

    def set_pair(self, other):
        self.pair = other
        other.pair = self

    def sync_pair(self):
        if self.pair is not None:
            self.pair.amps = -1 * self.amps

    def __str__(self):
        return str(self.amps)


class Node:
    # A node connects to A Singular Terminal of an Element
    # And can connect to multiple other nodes
    def __init__(self, parent_element, voltage=0, links=None):
        # Voltage level at the node
        self.V = Potential(voltage)

        # Current Flowing Into Element
        self.I = Current()

        self.parent = parent_element

        self.nodes = links
        if links is None:
            self.nodes = []

    def propagate_current(self, i):
        self.set_current(i)
        num_children = len(self.nodes)

        self.other_node().disconnect()

        for node in self.nodes:

            if node.parent is None or node.other_node().parent is None:
                continue
            node.other_node().propagate_current( i / num_children)

        self.other_node().reconnect(self.parent)

    def link_nodes(self, other):
        self.I.set_pair(other.I)

    def add(self, node):
        if node not in self.nodes:
            self.nodes.append(node)

    def get_current(self):
        return self.I.get_amps()

    def set_current(self, i):
        self.I.set_amps(i)

    def get_voltage(self):
        return self.V.volts

    def set_voltage(self, v):
        self.V.volts = v

    def other_node(self):
        for node in self.parent.get_nodes():
            if node is not self:
                return node
    def disconnect(self):
        self.parent = None

    def is_disconnected(self):
        if self.parent is None:
            return True
        return False

    def reconnect(self, parent):
        self.parent = parent

    def __str__(self):
        # return f"ID: {hex(id(self))}\nVoltage: {self.V}\nLinks To: {[i.parent for i in self.nodes]}\n"
        return f"Voltage: {self.V}\nCurrent: {self.I}\nLinks To: {[i.parent for i in self.nodes]}\n"


class CircuitElement:
    def __init__(self, voltage_a=0, voltage_b=0):
        self.A = Node(self, voltage_a)
        self.B = Node(self, voltage_b)
        self.A.link_nodes(self.B)

    def connect(self, other):
        for parent_node in [self.B] + self.B.nodes:
            for child_node in [other.A] + other.A.nodes:
                parent_node.add(child_node)
                child_node.add(parent_node)

    def get_voltage(self):
        return self.B.V - self.A.V

    def simulate(self):
        print("Beginning Simulation")
        # self.B.disconnect()
        self.A.propagate_current(9)
        # self.B.reconnect(self)
        print(f"{self.is_balanced()= }")

    def is_balanced(self):
        potential = self.A.get_voltage()

        # will not work for multiple children nodes
        next_node = self.A.nodes[0]
        next_element = next_node.parent

        while next_element != self:
            potential -= next_element.voltage_drop()

            # will not work for multiple children nodes
            next_node = next_node.nodes[0]
            next_element = next_node.parent
            # print(next_element)
            # return "F"

        return potential - self.B.get_voltage()

    def voltage_drop(self):
        return -1 * self.get_voltage()

    def get_nodes(self):
        return [self.A, self.B]

    def __str__(self):
        return "Node A:\n" + indent(self.A.__str__()) + "Node B:\n" + indent(self.B.__str__())
        # return indent(self.A.__str__())

    def __repr__(self):
        return "Circuit_Element"


class IdealResistor(CircuitElement):
    def __init__(self, resistance):
        super().__init__()
        self.R = resistance

    def voltage_drop(self):
        return self.R * self.A.get_current()

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

    # Single Resistance
    # v1.connect(r1)
    # r1.connect(v1)

    # Double Series Resistance
    # v1.connect(r1)
    # r1.connect(r2)
    # r2.connect(v1)

    # Double Parallel
    v1.connect(r1)
    v1.connect(r2)
    r1.connect(v1)
    r2.connect(v1)

    v1.simulate()

    print(v1)
    print(r1)
    print(r2)
    # print(r3)

    # print(f"{r3.get_current()}")


if "__main__" == __name__:
    main()
