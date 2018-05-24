# Main file for running Simulations

import math
import numpy as np

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
        # Take in ket like '10101' and then turn into |10101>. Must reverse string
        if len(instate) != self.qbits:
            print('Error: Qbit length does not match')
            return
        
        if type(instate) is str:
            instate = list(map(int,instate[::-1]))
            num = 0
            for i in range(self.qbits):
                num += instate[i] * (2 ** i)
            
        elif type(instate) is int:
            num = instate
            
        self.state = [0 for x in range(2 ** self.qbits)]
        self.state[num] = 1    

    # Get binary
    def getBinary(self, n, digits):
        return '{{:0{}b}}'.format(digits).format(n)

    # Map the integer n onto a set of locations for binary 0s and 1s and return new integer
    def mapBinaryPos(self, n, positions):
        ans = 0
        for i in range(len(positions)):
            ans += ((n >> i) & 1) * (2 ** positions[i])
        return ans

    # Operators stored here, 
    invsqrt2 = 1 / math.sqrt(2)
    gates = {
        'had': [[invsqrt2, invsqrt2], [invsqrt2, -invsqrt2]],
        'sx': [[0,1],[1,0]],
        'sy': [[0, complex(0, -1)], [complex(0, 1), 0]],
        'sz': [[1, 0], [0, -1]],
        'cnot': [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]],
        'swap': [[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]]
    }
    
    # Apply a matrix to a subset of total system.
    def actMatrix(self, m, bits):
        other_bits = sorted(list(set(range(self.qbits)) - set(bits)))
        add_kets = [self.mapBinaryPos(x, bits) for x in range(2 ** len(bits))]
        # For each possible configuration of unaffected bits, we calculate the matrix product for the affected bits
        for i in range(2 ** len(other_bits)):
            base_ket = self.mapBinaryPos(i, other_bits)
            kets = [base_ket + add_ket for add_ket in add_kets]
            cs = [self.state[ket] for ket in kets]
            # Calculate new kets
            newkets = (np.matrix(m) @ np.matrix(cs).T)
            # Assign them in the right place
            for j in range(len(add_kets)):
                self.state[base_ket + add_kets[j]] = complex(newkets[j])
                
    # Run the circuit
    def runCircuit(self, verbose = False):
        # Apply each operation in order
        for op in self.ops:
            if op[0] in self.gates:
                matrix = self.gates[op[0]]
                bits = op[1]
                if type(bits) is int:
                    bits = [bits]
                if len(matrix[0]) > 2:
                    self.actMatrix(matrix, bits)
                else:
                    for bit in bits:
                        self.actMatrix(matrix, [bit])
            else:
                print('{} gate not found'.format(op[0]))

            # Verbose mode
            if verbose:
                print('After: {}'.format(op))
                self.printState()

    # Print state
    def printState(self):
        accuracy = 6
        print('State: ')
        for ket in range(len(self.state)):
            c = self.state[ket]
            out = ''
            out += '|{} = {}> '.format(self.getBinary(ket, self.qbits), ket)
            if c.real == 0 and c.imag == 0:
                out += ' 0' + (accuracy + 1) * ' '
            else:
                if c.real != 0:
                    out += '{:+6f}'.format(c.real)
                if c.imag != 0:
                    out += '{:+6f}j'.format(c.imag)
            print(out)
                
if __name__ == "__main__":
    # Example useless system
    qs = QuantumSystem(3)
    qs.setInput('010')
    qs.printState()
    qs.addGate(('had', 1))
    qs.addGate(('swap', [1, 0]))
    qs.addGate(('sy', [2]))
    qs.viewCircuit()
    qs.runCircuit(True)
    print('Final: ')
    qs.printState()
