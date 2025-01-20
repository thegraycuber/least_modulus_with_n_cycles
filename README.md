This repository is intended to calculate terms for the following two OEIS sequences:  
[A379423](https://oeis.org/A379423) - Least modulus k such that (Z/kZ)* is the direct product of n nontrivial cyclic groups.  
[A379424](https://oeis.org/A379424) - Least modulus k such that (Z/kZ)* has a difference of n nontrivial cycles between its minimal and maximal representation.  
I made [this video](https://youtu.be/jCfoeqmQNeQ?si=XQLxhC8ALgTaX2gj) that explains these sequences in more depth.  

The file least_modulus_with_n_cycles.py is a fairly straightforward program that can find a few dozen terms of these sequences. It is far to slow to get many more terms though.

I optimized this in two sections:  
main.rs is used to generate a list of primes ordered by ln(p) / (# of cycles in U_p)  
infinite_knapsack.py uses this list to compute the terms of the sequence.  

This optimization is able to find a million terms of A379423 in only a few hours - far better than the naive first solution.
