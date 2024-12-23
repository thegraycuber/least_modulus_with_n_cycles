
import math

def add_prime(prime):
    test_number = prime[-1][0] + 1
    
    while True:
        p = 0
        is_prime = True
        while prime[p][0] ** 2 <= test_number:
            if test_number % prime[p][0] == 0:
                is_prime = False
                break
            p += 1

        if is_prime:
            cycles, prime = get_prime_fact(test_number-1,prime)
            prime.append([test_number,len(cycles)])
            return(prime)
        test_number += 1


def get_prime_fact(m,prime):

    m_current = m
    current_prime = 0
    prime_output = [[0]]
    while m_current > 1:
        if len(prime) <= current_prime:
            prime = add_prime(prime)

        while m_current % prime[current_prime][0] == 0:
            if prime_output[-1][0] == prime[current_prime][0]:
                prime_output[-1][1] += 1
            else:
                prime_output.append([prime[current_prime][0],1])

            m_current = int(m_current/prime[current_prime][0])

        current_prime += 1

    prime_output.pop(0)

    return(prime_output,prime)


def least_with_n_cycles(prime,limit,include_even = True):

    smallest_k = [1]

    k = 3
    while k < limit:

        k_factors, prime = get_prime_fact(k,prime)
        cycles = 0
        f = 0
        if k_factors[0][0] == 2:
            if include_even:
                cycles = min(2,k_factors[0][1]-1)
            f = 1
        p_val = 0
        while f < len(k_factors):
            while prime[p_val][0] < k_factors[f][0]:
                p_val += 1
            cycles += prime[p_val][1]
            if not include_even:
                cycles -= 1
            if k_factors[f][1] > 1:
                cycles += 1
            f += 1

        if len(smallest_k) <= cycles:
            smallest_k.append(k)
            print(k)
        
        k += 1

            
    return smallest_k
            
prime = [[2,0],[3,1]]
print(least_with_n_cycles(prime,100000))