/*
This program is used for the first half of finding terms for these two sequences:
https://oeis.org/A379423
https://oeis.org/A379424

The output has rows of this form:
( p, cycles, cost, value )
where p is a prime power
cycles is the maximum number of cycles in a representation of (Z/pZ)* (only odd cycles for A379424)
cost is ln(p)/cycles
and value is ln(p)

The output should be order ascending by cost, and there should be some real number r such that
every prime power with cost < r is in the output
and every prime power with cost > r is not in the output
*/

use std::{fs::File, u128};
extern crate csv;
use csv::WriterBuilder;
//use std::time;

fn primes_below_limit(primes: &mut Vec<bool>,limit: usize) {
    
    //generates a vector of all integers up to limit, true for prime, false for composite
    //this uses the sieve of eratosthenes

    let mut small_primes: Vec<usize> = vec![2,3,5];
    assert_eq!(vec![false,true,false,false,false,true],*primes); //primes should be input with 6 values
    let mut current_len: usize = primes.len(); 
    let mut next_small: usize = 5; 
    
    //process each small prime until the size would exceed limit
    while primes.len()*next_small <= limit {
    
        //add copies of the current values, to multiply the length by next_small
        for _ in 1..next_small{
            for j in 0..current_len{
                primes.push(primes[j]);
            }
        }
        
        //mark multiples of next_small as composites
        for i in (1..current_len).rev() {
            if primes[i]{
                primes[i*next_small] = false;
            }
        }

        println!("Sieve at {}",primes.len());
        
        //find the following small prime
        while !primes[next_small]{
            next_small += 1;
        }
        small_primes.push(next_small);
        current_len = primes.len();
    }
    
    //once highest primorial is reached, fill the rest of the vector
    for _ in 1..next_small{
        for j in 0..current_len{
            if primes.len() == limit{
                break;
            }
            primes.push(primes[j]);
        }
        if primes.len() == limit{
            break;
        }
    }
    
    //finish the sieve, checking up to the square root of the limit
    let max_small = (limit as f64).sqrt() as usize;
    
    while next_small <= max_small{
        
        for i in (1..limit/next_small as usize + 1).rev() {
            if primes[i]{
                primes[i*next_small] = false;
            }
        }
        
        while !primes[next_small]{
            next_small += 1;
        }
        small_primes.push(next_small);
    }
    
    //set the low values to be correct
    primes[1] = false;
    for i in small_primes{
        primes[i] = true;
    }
    
    
}


fn indices_extend(indices: &mut Vec<Vec<usize>>, prime_values: &Vec<u128>, index_needed: usize){

    // indices store which primes divide each number
    // for example, indices[14] = [0,3] since the 0th and 3rd prime divide 14

    // this is used to make sure indices is long enough
    if indices.len() > index_needed{return;} //return if already long enough

    let extend_count: usize = 1 + index_needed - indices.len();
    for _ in 0..extend_count{

        let mut remaining: u128 = indices.len() as u128; // going to divide this down by primes we find
        indices.push(vec![]);
        let mut prime_index: usize = 0;
        let last_index: usize = indices.len()-1;

        while remaining > 1{
            
            if remaining % prime_values[prime_index] == 0{
                indices[last_index].push(prime_index);
                while remaining % prime_values[prime_index] == 0{
                    remaining /= prime_values[prime_index];
                }
            }

            prime_index += 1;
        }
    }
}


fn generate_factor_list(primes: &Vec<bool>,only_odd: bool,file_path: &str){

    /* the factor list has the following two rows for each prime:
        ( prime, c, ln(prime)/c, ln(prime) )
        ( prime, 1, ln(prime)/1, ln(prime) )
        where c = the number of primes dividing (prime - 1)

        these will be called 
        ( factor, cycles, cost, value )

        the output should be sorted by cost and should be 'complete'
        i.e. there should be some real number r such that any row with cost < r is included in the list
        and any row with cost >= r is excluded from the list

        we also include ( 8, 2, ln(8)/2, ln(8) ) because ~group theory~ but that can be predefined
        predefine 8 and the fermat primes, the only with 1 cycle, since prime - 1 must be even
    */
    let mut factors: Vec<(u128,usize,f64,f64)>;
    let odd: usize;
    if !only_odd {
        factors = vec![
            (8,2,0.0,0.0),
            (3,1,0.0,0.0),
            (5,1,0.0,0.0),
            (17,1,0.0,0.0),
            (257,1,0.0,0.0),
            (65537,1,0.0,0.0)
        ];
        odd = 0;
    } else {
        factors = vec![
            (9,1,0.0,0.0),
            (25,1,0.0,0.0),
            (289,1,0.0,0.0),
            (66049,1,0.0,0.0),
            (4295098369,1,0.0,0.0)
        ];
        odd = 1;
    }

    for f in &mut factors{
        f.3 = (f.0 as f64).ln();
        f.2 = f.3/(f.1 as f64);
    }


    // primes is a list of true false, so we can use it check big primes up to (primes.len()-1)^2
    let big_prime_limit: u128 = (primes.len() as u128 -1)*(primes.len() as u128 -1);
    let mut prime_values: Vec<u128> = vec![2]; 
    for p in 3..primes.len(){
        if primes[p]{
            prime_values.push(p as u128);
        }
    }

    
    // for any nth primorial above big_prime_limit, we cannot check any primes with n cycles
    // thus the max cycles is the index of highest primorial less than big_prime_limit
    let mut max_cycles: usize = 0;
    let mut primorial: u128 = 2;
    while primorial <= big_prime_limit{
        max_cycles += 1;
        primorial *= prime_values[max_cycles];
    }

    /*  max_cost is the value determining inclusion and exclusion from the list

        we will not check any values >= big_prime_limit
        the minimum cost we may miss is ln(big_prime_limit)/max_cycles
        thus the max_cost cannot be any higher or we may not have a complete list

        similarly, we will miss any primes with n cycles where n > max_cycles. 
        the minimum possible cost of such a prime is ln(nth primorial)/n, with n = max_cycles + 1
        this also gives an upper bound for the max_cost

        take the minimum of these two values.   */
    let max_cost: f64 = ((big_prime_limit as f64).ln()/((max_cycles - odd) as f64)).min((primorial as f64).ln()/((max_cycles - odd) as f64 + 1.0));


    // then take exp so we can compare against prime rather than ln(prime)
    let max_per_cycle: f64 = max_cost.exp();
    let mut current_max: f64 = max_per_cycle;

    // fill the results with the rows ( prime, 1, ln(prime)/1, ln(prime) )
    let mut fermat_exclude: Vec<u128> = vec![];
    if only_odd { fermat_exclude = vec![3,5,17,257,65537];} // if only_odd, we exclude rows with fermat primes

    for p in 1..prime_values.len() {
        if prime_values[p] as f64 > max_per_cycle{break;}
        if fermat_exclude.contains(&prime_values[p]) {continue;}
        let ln_check: f64 = (prime_values[p] as f64).ln();
        factors.push((prime_values[p],1,ln_check,ln_check));
    }

    // this will be explained where it is used
    let mut indices: Vec<Vec<usize>> = vec![
        vec![],
        vec![],
        vec![0]
    ];

    /*
        in the following section we loop cycles from 2 to max_cycles
        and check all values that would give that number of cycles.
        if prime, add to the results list ( prime, c, ln(prime)/c, ln(prime) )

        for example, when cycles = 3 we check all n such that
        n - 1 is divisible by exactly 3 primes

        this is done using a boolean vector called prime_grid
        [true, false, false, true] corresponds to 14
        indexes 0 and 3 are true, and 14 is the product of the 0th and 3rd prime

        always keep index 0 true since any prime is odd
        otherwise, to increment prime_grid, find the first 'chunk' of trues
        push the highest true up one, and bring the rest back to index 1

        [true, false, false, false,  true,  true,  true, false,  true]
        increments to
        [true,  true,  true, false, false, false, false,  true,  true]

        if prime_grid looks like:
        [true, true, ... true, false, false, ... false, true]
        then any future increment will be higher.
        therefore if the product > max, then exit
        exit_allowed = prime_grid looks like this
     */

    // prep variables
    primorial = 1; // set primorial for starting position
    let mut prime_grid: Vec<bool>; // current primes to include in test
    let mut min_false: usize; // index of smallest false in prime_grid
    let mut final_prime: usize; // index of last included prime, not stored in prime_grid for easier logic
    let mut product_without_final: u128; // product of primes to test, excluding final prime
    let mut exit_allowed: bool;

    for cycles in 2..max_cycles+1{

        prime_grid = vec![true;cycles-1]; // this has length cycles-1 since the final prime is stored separately
        min_false = prime_grid.len();
        primorial *= prime_values[cycles-2]; // product of first cycles-1 primes
        product_without_final = primorial; 
        println!("Checking {} cycles",cycles);
        current_max *= max_per_cycle;
       
        exit_allowed = true; 


         // loop through all states of prime_grid
        loop{
            
            final_prime = prime_grid.len(); // final prime starts at smallest prime past prime_grid
            let mut prime_product: u128 = product_without_final*prime_values[final_prime]; // full product

            if (prime_product + 1) as f64 > current_max && exit_allowed{
                break
            }

            // increment final_prime until max is exceeded
            while (prime_product + 1) as f64 <= current_max{

                /* multiplier is used to check for prime powers
                    for example, 61 has 3 cycles, since 60 is divisible by 2, 3, and 5
                    but if we check 2*3*5 + 1 we just get 31 and miss 61.
                    so we must check multiples of 30 + 1 to find all primes
                    we check 31, 61, 91, 121, 151, 181... but not 211 because that would introduce a new prime
                */

                let max_multiplier: usize = (current_max/(prime_product as f64)) as usize;
                for multiplier in 1..(max_multiplier+1){

                    // indices store which primes divide each number
                    // for example, indices[14] = [0,3] since the 0th and 3rd prime divide 14
                    indices_extend(&mut indices, &prime_values,multiplier);
                
                    // see if the index is bad (introduces an new prime and thus increasing cycle #)
                    // a good index only uses primes from prime_grid and final_prime
                    let mut bad_index: bool = false;
                    for m in 0..indices[multiplier].len(){
                        if indices[multiplier][m] >= prime_grid.len(){
                            if indices[multiplier][m] != final_prime{
                                bad_index = true;
                                break;
                            }
                        } else if !prime_grid[indices[multiplier][m]]{
                            bad_index = true;
                            break;
                        }

                    }

                    if bad_index{continue;}
                    
                    // check if the value is prime
                    let check_value: u128 = (multiplier as u128)*prime_product + 1;      
                    let mut check_is_prime: bool = true;
                    // if possible, just check primes for true/false
                    if (primes.len() as u128) > check_value{
                        check_is_prime = primes[check_value as usize];

                    // if too large, we've got work to do.
                    } else {
                        //max_grid = max_grid.max(prime_grid.len());

                        // check some small primes to quickly rule out composites
                        for p in min_false..prime_grid.len(){

                            if prime_grid[p]{
                                continue;
                            }
                            if check_value % prime_values[p] == 0{
                                check_is_prime = false;
                                break;
                            }
                        }

                        // run a fermat primality test on 2^p-1 to rule out more composites
                        if check_is_prime{

                            let mut exp_2_2: u128 = 2;
                            let mut exp_2_ord: u128 = 1;
                            let mut remaining_order: u128 = (check_value - 1)/2;

                            while remaining_order > 0 {
                                exp_2_2 = (exp_2_2 * exp_2_2) % check_value;
                                if remaining_order % 2 == 1{
                                    remaining_order -= 1;
                                    exp_2_ord = (exp_2_ord * exp_2_2) % check_value; 
                                }
                                remaining_order /= 2;
                            }

                            if exp_2_ord != 1{
                                check_is_prime = false;
                            }
                            
                        }
                        

                        // confirm remaining primes by checking for divisibility
                        if check_is_prime{
                            let p_limit = (check_value as f64).sqrt() as u128 + 1;
                            for p in prime_grid.len()..prime_values.len(){
                                if p_limit < prime_values[p]{
                                    break;
                                }
                                if check_value % prime_values[p] == 0{
                                    check_is_prime = false;
                                    break;
                                }
                            }
                            
                        }

                    }

                    // if we found a prime, add it to the results list
                    if check_is_prime{
                        let ln_check: f64 = (check_value as f64).ln();
                        factors.push((check_value,cycles-odd,ln_check/((cycles-odd) as f64),ln_check));
                    }

                }

                final_prime += 1;
                //prime_values_extend(&mut prime_values,&primes,final_prime);
                prime_product = product_without_final*prime_values[final_prime];

            }


            // next we will increment prime_grid

            // if cycles = 2, then prime_grid = [true]. we already checked any 2*p + 1 so we can break
            if cycles == 2 {break;}

            exit_allowed = false;
            // if min_false == 1, we'll need to find the first chunk of trues (recall prime_grid[0] is always true, we need an even number since we add 1)
            if min_false == 1{
                let mut min_true: usize = 1;
                while !prime_grid[min_true]{
                    min_true += 1;
                }
                // once the first chunk is found, find the end of chunk
                let mut max_true: usize = min_true;
                while prime_grid.len() > max_true + 1 && prime_grid[max_true+1]{
                    max_true += 1;
                }
                min_false = max_true + 1;

                // move down all trues except the highest
                max_true -= 1;
                let mut mover: usize = 1;
                while !prime_grid[mover] && prime_grid[max_true] && mover < max_true{
                    prime_grid[mover] = true;
                    prime_grid[max_true] = false;
                    product_without_final = product_without_final*prime_values[mover]/prime_values[max_true];
                    mover += 1;
                    max_true -= 1;
                }
            }

            // if the min_false is at the end, we need to extend prime_grid. also, we're allowed to exit
            if min_false == prime_grid.len(){
                println!("Done checking {} cycles options with {} as penultimate prime",cycles,prime_values[prime_grid.len()-1]);
                prime_grid.push(true);
                exit_allowed = true;
            }
            // move up the true and adjust the product
            prime_grid[min_false-1] = false;
            prime_grid[min_false] = true;
            product_without_final = product_without_final*prime_values[min_false]/prime_values[min_false-1];

            // if cycles == 3, prime_grid always looks like [true, false, ... false, true] and always exit allowed
            if cycles == 3 {
                min_false = prime_grid.len();
                continue;
            }

            // drop min_false until it's right above a true
            while min_false > 0 && !prime_grid[min_false-1]{
                min_false -= 1;
            }
        }

    }

    // sort factors and remove anything with a cost that is too high
    factors.sort_by( |a: &(u128, usize, f64, f64), b: &(u128, usize, f64, f64)| a.2.partial_cmp(&b.2).unwrap());
    while factors.last().unwrap().2 > max_cost{
        factors.pop();
    }

    // csv code below thanks to https://gistlib.com/rust/create-a-csv-file-in-rust
    // Create our file object
    let file = File::create(file_path).expect("Unable to create file");

    // Create our CSV writer using the builder
    let mut csv_writer = WriterBuilder::new()
        .delimiter(b',')
        .quote_style(csv::QuoteStyle::NonNumeric)
        .from_writer(file);

    // Write our data to the CSV file
    for factor in factors{
        csv_writer.write_record(&[factor.0.to_string(),factor.1.to_string(),factor.2.to_string(),factor.3.to_string()]).expect("Unable to write record");
    }

}


fn main(){
    
    //let now = time::Instant::now();
    let mut primes: Vec<bool> = vec![false,true,false,false,false,true]; // boolean vector of primes, index n = (n is prime)

    
    let limit: usize = 2000000; // the length that we will extend 'primes' to
    primes_below_limit(&mut primes,limit);
    generate_factor_list(&primes,false,"A379423_factors.csv");
    

    /*
    let limit: usize = 500000; // Lower for A379424 since it takes much longer
    primes_below_limit(&mut primes,limit);
    generate_factor_list(&primes,true,"A379424_factors.csv");
    */

    //println!("{}",now.elapsed().as_millis());
}

