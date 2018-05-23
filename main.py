# Main file for running Simulations

import math

class QuantumSystem:

    def __init__(self, qbits, rep = 'kets'):
        # Number of total qbits in the system
        self.qbits = qbits

        # Method of representing the state of the system, kets vs MPS
        self.rep = rep

        self.resetCircuit()

    def resetCircuit(self):
        # List of gate operations
        # Operations are of form (GATE NAME, op1, op2, ....)
        self.ops = []

        # Coefficients in front of each ket, start in state |0...0>
        if self.rep == 'kets':
            self.state = [0 for x in range(2 ** self.qbits)]
            self.state[0] = 1

    # Add a gate into the circuit
    def addGate(self, gate, index = None):
        if index is None:
            self.ops.append(gate)
        else:
            self.ops.insert(index, gate)

    # View gates in the circuit
    def viewCircuit(self):
        print('Circuit: ')
        print(self.ops)

    # Remove gate from circuit
    def removeGate(self, index = None):
        if index is None:
            self.ops.pop()
        else:
            del self.ops[index]

    # Take in list of qbits long, and set that as initial state
    def setInput(self, instate):
        if len(instate) != self.qbits:
            print('Error: Qbit length does not match')
            return
        num = 0
        for i in range(self.qbits):
            num += instate[i] * (2 ** i)
            
        self.state = [0 for x in range(2 ** self.qbits)]
        self.state[num] = 1
        
    # Run the circuit
    def runCircuit(self, verbose = False):
        # Operators stored here, TODO move, rename later
        invsqrt2 = 1 / math.sqrt(2)
        matrices = {
            'had': [[invsqrt2, invsqrt2], [invsqrt2, -invsqrt2]],
            'sx': [[0,1],[1,0]],
            'sy': [[0, complex(0, -1)], [complex(0, 1), 0]],
            'sz': [[1, 0], [0, -1]]
        }
        
        # Apply each operation in order
        for op in self.ops:
            if op[0] in matrices:
                matrix = matrices[op[0]]
                bits = op[1]
                if type(bits) is int:
                    bits = [bits]
                # Apply to each bit individualy
                for bit in bits:
                    newstate = [0 for x in range(2 ** self.qbits)]
                    # Apply to each ket coefficient
                    for ket in range(len(self.state)):
                        c = self.state[ket]
                        bitval = (ket >> bit) % 2
                        oppket = ket ^ (1 << bit) # Oppket is ket with bit flipped
                        
                        newstate[ket] += matrix[bitval][bitval] * c
                        newstate[oppket] += matrix[1 - bitval][bitval] * c

                    # New value
                    self.state = newstate
            else:
                print('{} gate not found'.format(op[0]))

            # Verbose mode
            if verbose:
                self.printState()

    # Print state
    def printState(self):
        print('State: ')
        for ket in range(len(self.state)):
            c = self.state[ket]
            print('{{:+f}} |{{:0{}b}}>'.format(self.qbits).format(c, ket))
                
if __name__ == "__main__":
    # Example useless system
    qs = QuantumSystem(2)
    qs.printState()
    qs.setInput([0,1])
    qs.addGate(('had', [0, 1]))
    qs.addGate(('sy', 0))
    qs.addGate(('sz', 1))
    qs.addGate(('had', 0))
    qs.viewCircuit()
    qs.runCircuit(True)
    print('Final: ')
    qs.printState()
