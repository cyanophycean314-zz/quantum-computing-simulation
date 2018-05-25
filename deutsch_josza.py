import qcs

# Map |x>|y> to |x>|y ^ f(x)> where y is 1 qbit
# Last q bit is the output
def constant_DJ(nqbits, result):
    return (lambda x: x ^ result)

# Let f(x) = x_k for some key qbit k. 
def balanced_DJ(nqbits, keyqbit):
    return (lambda x: x ^ ((x >> keyqbit) & 1))

qbits = 10
qs = qcs.QuantumSystem(qbits)

qs.set_input(1) #0..01
dj_func = constant_DJ(qbits, 1)
dj_matrix = qs.gen_matrix_oracle(qbits, dj_func)
qs.define_gate('oracle', dj_matrix)
qs.add_gate('had', range(qbits))
qs.add_gate('oracle', range(qbits))
qs.add_gate('had', range(1, qbits))
qs.add_gate('measure', range(1, qbits))
qs.view_circuit()
qs.run_circuit()
print('Final: ')
qs.print_state()
print('Balanced' if qs.get_last_msmt()[0] == 0 else 'Constant')
