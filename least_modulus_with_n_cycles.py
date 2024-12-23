
"""
This program is used to calculate the smallest integers k such that (Z/kZ)* can be represented as the direct product of n cyclic groups, for different values of n

For example, the 4th term is 56 because (Z/56Z)* ≅ C2 x C2 x C2 x C3 and there is no integer smaller than 56 with a representation as the product of 4 cyclic groups

(Z/kZ)* denotes the multiplicative group of integers modulo k
https://en.wikipedia.org/wiki/Multiplicative_group_of_integers_modulo_n#Structure

https://oeis.org/A379423
https://oeis.org/A379424

""" 


# list of primes, where each element is [p, # of primes dividing p-1] or in other words [p, max # of cycles whose product is isomorphic to (Z/pZ)*]
prime = [[2,0],[3,1]]

# add a number to the list of primes
def add_prime(prime):

    # starting checking 2 above the highest prime
    test_number = prime[-1][0] + 2
    
    # check until a prime is found
    while True:
        p = 0
        is_prime = True
        while prime[p][0] ** 2 <= test_number:
            if test_number % prime[p][0] == 0:
                is_prime = False
                break
            p += 1

        # if a prime p is found, add it to the list, along with the # of primes that divide p-1
        if is_prime:
            cycles, prime = get_prime_fact(test_number-1,prime)
            prime.append([test_number,len(cycles)])
            return(prime)

        test_number += 2


# get the prime factorization of m. Returns with primes and exponents
# the return value for m = 720 is [[2,4],[3,2],[5,1]]
def get_prime_fact(m,prime,odd_cube_return = False):

    current_prime = 0
    factors = [[0]]

    # use m_current to track value of m that hasn't been accounted for yet
    m_current = m 
    while m_current > 1:

        # add a prime to the list if needed
        if len(prime) <= current_prime:
            prime = add_prime(prime)

        while m_current % prime[current_prime][0] == 0:
            # if the current prime has already been tracked, add 1 to the count
            if factors[-1][0] == prime[current_prime][0]:
                factors[-1][1] += 1
                if odd_cube_return and current_prime > 0 and factors[-1][1] > 2:
                    return ([], prime)
            # otherwise, add a new element to track it
            else:
                factors.append([prime[current_prime][0],1])

            m_current = m_current // prime[current_prime][0]

        current_prime += 1

    # get rid of the [0] that is used to prevent an error when checking factors[-1][0] before anything is added
    factors.pop(0)

    return(factors,prime)


# Find the least moduli lower than the input limit
# include_even determines whether to count all cycles (A379423) or just the odd cycles (A379424)
def least_with_n_cycles(prime,limit,include_even = True):

    # the 0th index is 1
    smallest_k = [1]

    # k is the value we are checking
    k = 2
    while k < limit:

        k += 1
        # if only checking odds, an even k will never by the smallest
        if k % 2 == 0 and not include_even:
            continue
        # the smallest k will never be divisible by 16, k/2 would have the same cycle count
        if k % 16 == 0:
            continue

        k_factors, prime = get_prime_fact(k,prime,True)
        # k_factors returns empty if k is divisible by the cube of an odd prime p, since k/p would have the same cycle count
        if len(k_factors) == 0:
            continue
        cycles = 0
        f = 0

        # if k is divisible by 2, adjust f to skip the 2 power, and set cycles to 2 if divisible by 8, 1 is only 4, and 0 if only 2
        if k_factors[0][0] == 2:
            cycles = min(2,k_factors[0][1]-1)
            f = 1

        # for each prime dividing k, add the cycles from that primes unit group, plus 1 if the prime is a square, minus 1 if excluding even cycles
        p_val = 0
        while f < len(k_factors):
            while prime[p_val][0] < k_factors[f][0]:
                p_val += 1
            cycles += prime[p_val][1]
            if not include_even:
                cycles -= 1
            if k_factors[f][1] == 2:
                cycles += 1
            f += 1

        # if the cycles is higher than all prior, track k as the smallest with n
        if len(smallest_k) <= cycles:
            smallest_k.append(k)
            print(k)
        
    return smallest_k

print(least_with_n_cycles(prime,100000))