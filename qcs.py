# Main file for running Simulations

import math
import numpy as np

class QuantumSystem:

    def __init__(self, qbits, rep = 'kets'):
        # Number of total qbits in the system
        self.qbits = qbits

        # Method of representing the state of the system, kets vs MPS
        self.rep = rep

        self.reset_circuit()

    def reset_circuit(self):
        # List of gate operations
        # Operations are of form (GATE NAME, op1, op2, ....)
        self.ops = []

        # Coefficients in front of each ket, start in state |0...0>
        if self.rep == 'kets':
            self.set_new_state(0)

    # Set new state
    def set_new_state(self, new_state):
        self.state = [0 for x in range(2 ** self.qbits)]
        self.state[new_state] = 1

    # Add a gate into the circuit
    def add_gate(self, gate, bits, index = None):
        if index is None:
            self.ops.append((gate, bits))
        else:
            self.ops.insert(index, (gate, bits))

    # View gates in the circuit
    def view_circuit(self):
        print('Circuit: ')
        print(self.ops)

    # Remove gate from circuit
    def remove_gate(self, index = None):
        if index is None:
            self.ops.pop()
        else:
            del self.ops[index]

    # Take in list of qbits long, and set that as initial state
    def set_input(self, instate):
        if type(instate) is str:
            # Take in ket like '10101' and then turn into |10101>. Must reverse string
            if len(instate) != self.qbits:
                print('Error: Qbit length does not match')
                return

            instate = list(map(int,instate[::-1]))
            num = 0
            for i in range(self.qbits):
                num += instate[i] * (2 ** i)            
        elif type(instate) is int:
            num = instate

        self.set_new_state(num)

    # Get binary
    def get_binary(self, n, digits):
        return '{{:0{}b}}'.format(digits).format(n)

    # Map the integer n onto a set of locations for binary 0s and 1s and return new integer
    def map_binary_pos(self, n, positions):
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
    def act_matrix(self, m, bits):
        other_bits = sorted(list(set(range(self.qbits)) - set(bits)))
        add_kets = [self.map_binary_pos(x, bits) for x in range(2 ** len(bits))]
        # For each possible configuration of unaffected bits, we calculate the matrix product for the affected bits
        for i in range(2 ** len(other_bits)):
            base_ket = self.map_binary_pos(i, other_bits)
            kets = [base_ket + add_ket for add_ket in add_kets]
            cs = [self.state[ket] for ket in kets]
            # Calculate new kets
            newkets = (np.matrix(m) @ np.matrix(cs).T)
            # Assign them in the right place
            for j in range(len(add_kets)):
                self.state[base_ket + add_kets[j]] = complex(newkets[j])

    # Measure subset of qbits
    def measure_qbits(self, qbits, verbose):
        probabilities = [abs(c) * abs(c) for c in self.state]
        other_bits = sorted(list(set(range(self.qbits)) - set(qbits)))
        add_kets = [self.map_binary_pos(x, qbits) for x in range(2 ** len(qbits))]
        probs = {}
        for add_ket in add_kets:
            prob = 0
            for i in range(2 ** len(other_bits)):
                base_ket = self.map_binary_pos(i, other_bits)
                prob += probabilities[base_ket + add_ket]
            probs[add_ket] = prob
        self.last_measure_prob = probs
        
        new_state = int(np.random.choice(2 ** self.qbits, 1, p = probabilities))
        if verbose:
            print(new_state)
        self.set_new_state(new_state)
        return prob

    # Get the object
    def get_last_msmt(self):
        return self.last_measure_prob

    # Print it out
    def print_last_msmt(self):
        print('Last measurement: ')
        for add_ket in self.last_measure_prob:
            p = self.last_measure_prob[add_ket]
            if p != 0:
                print('|{}> = {}'.format(self.get_binary(add_ket, len(self.last_measure_prob).bit_length() - 1), p))
    
    # Run the circuit
    def run_circuit(self, verbose = False):
        # Apply each operation in order
        for op in self.ops:
            if op[0] in self.gates:
                matrix = self.gates[op[0]]
                bits = op[1]
                if type(bits) is int:
                    bits = [bits]
                if len(matrix[0]) > 2:
                    self.act_matrix(matrix, bits)
                else:
                    for bit in bits:
                        self.act_matrix(matrix, [bit])
            # Measure some subset of qbits
            elif op[0] == 'measure':
                qbits = op[1]
                self.measure_qbits(op[1], verbose)
            else:
                print('{} gate not found'.format(op[0]))

            # Verbose mode
            if verbose:
                print('After: {}'.format(op))
                self.print_state()

    # Print state
    def print_state(self):
        accuracy = 6
        print('State: ')
        for ket in range(len(self.state)):
            c = self.state[ket]
            out = ''
            out += '|{} = {}> '.format(self.get_binary(ket, self.qbits), ket)
            if c.real == 0 and c.imag == 0:
                out += ' 0' + (accuracy + 1) * ' '
            else:
                if c.real != 0:
                    out += '{:+6f}'.format(c.real)
                if c.imag != 0:
                    out += '{:+6f}j'.format(c.imag)
            print(out)

    # Define a new gate
    def define_gate(self, name, matrix):
        self.gates[name] = matrix

    # Generate matrix based off oracle function
    def gen_matrix_oracle(self, nqbits, func):
        matrix = None
        for i in range(2 ** nqbits):
            result = func(i)
            if type(result) is int:
                out = [[0] for _ in range(2 ** nqbits)]
                out[result] = [1]
            elif type(result) is list:
                out = [[x] for x in result]

            if matrix is None:
                matrix = np.array(out)
            else:
                matrix = np.hstack((matrix, out))
        return matrix        
    
if __name__ == "__main__":
    # Example useless system
    qs = QuantumSystem(5)
    qs.set_input('00001')
    qs.print_state()
    qs.define_gate('rootnot', [[complex(.5, .5), complex(.5, -.5)], [complex(.5, -.5), complex(.5, .5)]])
    qs.add_gate('had', 1)
    qs.add_gate('rootnot', 0)
    qs.add_gate('swap', [1, 0])
    qs.add_gate('sy', [2])
    qs.view_circuit()
    qs.run_circuit(True)
    print('Final: ')
    qs.print_state()
