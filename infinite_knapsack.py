
"""
The Infinite Knapsack problem is a variation of the 0/1 Knapsack problem:
Suppose there is a set of items, each having a weight and value.
You also have a knapsack with a maximum weight capacity.
What is the maximum value of items that can be carried in that knapsack?

The Infinite Knapsack problem attempts to solve this problem when 
there are infinite items to choose from. How is this possible?

The technique below relies on using the 'cost' of each item, where
    cost = value/weight
and assumes that we can generate a finite list of items such that for some
real number r, all items with cost greater than r appear in the list,
and all items with cost lower than r do not.
We also assume that all weights are integers.

We can use such a list to find some terms in the sequence A with
    A(n) = maximum value with capacity of n 

This algorithm can be applied to find terms in the following sequences:
https://oeis.org/A379423
https://oeis.org/A379424
https://oeis.org/A380222

""" 

#import time
import sys
sys.set_int_max_str_digits(0)

def infinite_knapsack_terms(item_list,file_name,direction = 1):
 
    """
    The input item_list should have the following form for each row:
        [ name, weight, cost, value ]

    I'll denote item_list[i] as [ name_i, w_i, c_i, v_i ]
    
    item_list is expected to be sorted descending by cost.
    You can input -1 as direction for ascending instead, for a minimizing value problem.
    """



    """
    The idea of this algorithm is to base the sequence around a subset.
    Since item_list is sorted, the set of first i items First_i will be the 
    most valuable option that is at most weight s_i = sum(w_j for j <= i)
    Running across all values of i gives a subset of the sequence.

    We then build the rest of the sequence around this subset.
    To find the nth term, find i such that s_i < n <= s_i+1
    we take First_i as a starting point, and look to find the highest value 
    possible from taking advantage of the extra d = n - s_i of weight capacity 
    by checking different ways to 'subtract' items from First_i
    and 'add' items from outside of First_i.

    Let Sub_j be the least valuable subset of First_i with weight j
    and Add_j be the most valuable subset outside of First_i with weight j.
    Find the value r < s_i that maximizes: weight(Add_r+d) - weight(Sub_r)

    The most valuable set of items with weight n is all items in
    Add_r+d and all items in First_i but not Sub_r.

    We'll throw in a few tricks to make this process fast.
    """

    sequence_list = [[0,0]] # the output list
    subtract_list = [[0,[]]] # this has the current info for Sub_j, format [ total value, list of indices ]
    add_list = [[0,[],0,-1,0]] # this has the current info for Add_j, format [ total value, list of indices, final index, overflow indicator, final weight ]
    c_indices = [[]] # c_indices[a][0] is index of closest item with weight a. c_indices[a][1] is the following one, etc.

    # these will be explained when applied
    overflow_value = [0] 
    max1 = 1
    max2 = 2
    while max(item_list[0][1],item_list[1][1]) > item_list[max2][1]:
        max2 += 1

    # let's go!
    for i in range(len(item_list)-1):

        # incremental status update and output. It is better for subtract list length to be low, this provides updates
        if i % 1000 == 0:
            print('Checking item index',i,'   Subtract list length:',len(subtract_list))
            file_output(sequence_list,file_name)

        
        """
        Here we update add_list. 
        We're looking for the sets of highest value for each weight j.
        Conveniently, we have the add_list from the previous item.
        If that item was not part of add_list[a], then add_list[a] does not need an update.

        Otherwise, take z to be the index of the last item in add_list[a]. The lowest cost item.
        We don't know z yet.
        Let's consider add_list[a-w_z]. 

        Suppose the item_z is not in add_list[a-w_z].
        add_list[a-w_z] must be add_list[a] - item_z.
        Otherwise, add_list[a_w_z] + item_z would have higher value than add_list[a], 
        a contradiction by the definition of add_list.

        So if item_z is not in add_list[a-w_z], 
        we can check each add_list[a-b] + first unused item with weight = b, 
        taking the highest value to be add_list[a]

        But what if the item_z IS in add_list[a-w_z]?
        I've not encountered this, and therefore found it most simple just to assert that it's not true.
        If item_z WERE in add_list[a-w_z], then the following must be true:
            a > 2*w_z
            there is some y < z such that item_y is not in add_list[a-w_z]
        """

        add_list[0][2] = i-1 # default 'final' index for empty set. tells us where to start checking

        # use the length of a subtract list to inform how many items add_list needs
        add_max = len(subtract_list) + max(item_list[i][1],item_list[i+1][1])
        while add_max < len(add_list) and len(add_list) > 0:
            add_list.pop()

        for a in range(1,max(add_max,len(add_list))):
            if len(add_list) == a:
                add_list.append([])
            elif add_list[a][1][0] != i-1 or add_list[a][3] != -1: # continue if no update needed or already overflowed.
                continue
            
            z_checker = [] # used to assert z item isn't in add_list[a-w_z]

            for w_z in range(1,a+1): # check each option for final weight
                
                # find the first item with weight z after add_list[a-w_z][2], updating c_indices as needed
                if len(c_indices) == w_z:
                    c_indices.append([i-1])

                c_index = 0
                while c_indices[w_z][c_index] <= add_list[a-w_z][2]: 
                    c_index += 1
                    if len(c_indices[w_z]) == c_index:
                        new_c_index = c_indices[w_z][-1] + 1
                        while new_c_index < len(item_list) and item_list[new_c_index][1] != w_z:
                            new_c_index += 1
                        c_indices[w_z].append(new_c_index)

                # if the index overflowed, substitute overflow_value using the lowest cost within item_list
                if c_indices[w_z][c_index] >= len(item_list):
                    while len(overflow_value) <= w_z:
                        overflow_value.append(overflow_value[-1] + item_list[-1][2])
                    check_value = overflow_value[w_z]+add_list[a-w_z][0]
                    overflow = w_z
                else:
                    check_value = item_list[c_indices[w_z][c_index]][3]+add_list[a-w_z][0]
                    overflow = -1

                # if z_item might by in add_list[a-w_z], get upper bound of value
                if a > w_z*2 and add_list[a-w_z][4] == w_z and len(add_list[a-w_z][1]) > add_list[a-w_z][2] - i + 1:
                    z_upper_bound = add_list[a-w_z][0]+item_list[add_list[a-w_z][1][-1]][3] #TODO double check this
                    if len(z_checker) == 0 or z_checker[0]*direction < z_upper_bound*direction:
                        z_checker = [z_upper_bound,w_z]

                # update add_list[a] if appropriate
                if w_z == 1 or check_value*direction > add_list[a][0]*direction:
                    add_list[a] = [check_value,add_list[a-w_z][1].copy(),c_indices[w_z][c_index],max(overflow,add_list[a-w_z][3]),w_z]
                    add_list[a][1].append(add_list[a][2])

            # assert z item isn't in add_list[a-w_z]
            if len(z_checker) > 0 and z_checker[0]*direction > add_list[a][0]*direction:
                print(i,a,'WARNING: item_z may be in add_list[a-w_z]!',z_checker, add_list[a-z_checker[1]],add_list[a])
                return sequence_list

        # cleaning up c_indices
        for c in range(1,len(c_indices)):
            while c_indices[c][0] < i:
                c_indices[c].pop(0)


        """
        Alright, now we actually get to FIND the terms of the sequence!
        Loop delta from 1 to w_item, and find the most valuable way to increase weight by delta
        then write the result as the next term of the sequence.

        Since I want to use this to find millions of terms, I write using a shorthand.
        The nth row is written as relative to mth row, with m<n. The nth row looks like:
        [n, value, m, '+', a_1, a_2, ... a_x, '-', s_1, s_2, ... s_y]
        where a_j are names of items in the nth but not mth
        and s_j are names of items in the mth but not nth
        """

        last_index = len(sequence_list) - 1
        for delta in range(1,item_list[i][1]+1):

            max_value = [add_list[delta][0],0] # starting point, just add and no subtract

            # check each value to subtract
            for s in range(1,len(subtract_list)):
                if subtract_list[s][0] == -1: # if impossible to subtract this amount, skip
                    continue
                check_value = add_list[delta+s][0] - subtract_list[s][0]
                if max_value[0]*direction < check_value*direction: # update if new max
                    max_value = [check_value,s]

            if add_list[delta+max_value[1]][3] != -1: # if the max includes overflow, exit. item_list is too short to continue
                print('Overflowed from weight',add_list[delta+max_value[1]][3])
                return sequence_list
            
            # write the new term
            sequence_list.append([len(sequence_list),sequence_list[last_index][1]+max_value[0],last_index,'+'])
            for seq_factor in add_list[delta+max_value[1]][1]:
                sequence_list[-1].append(item_list[seq_factor][0])
            sequence_list[-1].append('-')
            for seq_factor in subtract_list[max_value[1]][1]:
                sequence_list[-1].append(item_list[seq_factor][0])
        

        """
        Now we update subtract_list for the next item. This is much easier than add_list.
        In fact, it uses the same technique as the finite knapsack problem.
        Given the new item's weight of w_i, the new is subtract_list[s] is either:
        the current subtract_list[s] or the current subtract_list[s-w_i] + i
        """
        
        s = len(subtract_list) - 1
        for new_sub in range(item_list[i][1]):
            subtract_list.append([-1,[]]) # we can subtract higher values with a new item to pick from

        # loop through items of subtract list that aren't just added, checking value if including new item lowers value
        while s > -1:
            check_value = subtract_list[s][0] + item_list[i][3] 
            if subtract_list[item_list[i][1]+s][0]*direction > check_value*direction or subtract_list[item_list[i][1]+s][0] == -1:
                subtract_list[item_list[i][1]+s] = [check_value,subtract_list[s][1].copy(),0]
                subtract_list[item_list[i][1]+s][1].append(i)
            s -= 1


        """
        Okay here comes another long text.
        (that was equally to prep you for reading and prep me for writing)
        We CAN check all possible combinations of add_list and subtract_list, but the further we go,
        the more there will be. If we want to get millions of terms quickly, we need to optimize this.

        This uses the principle that it's generally best to subtract a small amount. 
        Every item that we subtract has a higher cost than every item we add, so the more we subtract, the lower the ending value.
        For certain high values, we can prove that it will always be better to subtract some lower amount.

        max1 is the lowest index of an item higher weight than all previous rows of item_list, including i.
        In other words, it is the lowest index > i such that w_max1 >= w_j for all j < max1
        max2 is the next one, the lowest index > max1 such that w_max2 >= w_j for all j < max2

        Recall that c_i is the cost of the current item
        
        Given some s >= w_max1 + w_max2, we can delete subtract_list[s] if the following requirements hold:
        I)  value(subtract_list[s]) >= c_i * (s - x) + value(subtract_list[x]) 
            for all x such that w_max1 <= x < w_max1 + w_max2
        II) value(subtract_list[s]) > value(subtract_list[s-w_max1]) + v_max1
        III) value(subtract_list[s]) > value(subtract_list[s-w_(max1-1)]) + v_(max1-1)

        To show this, suppose we want to get a delta of d, meaning we'll add using add_list[s+d]

        Case 1: 
            there exists some subset A of items from add_list[s+d] such that:  w_max1 + d <= weight(A) < w_max1 + w_max2 + d
            Then:
                value(add_list[s+d]) - value(subtract_list[s])
            <=  value(A) + c_i*(s+d-weight(A)) - value(subtract_list[s])     because the items removed from add_list[s+d] have cost at most c_i
            <=  value(A) + c_i*(s+d-weight(A)) - c_i*(s-weight(A)+d) - value(subtract_list[weight(A)-d])      by the requirement I
            =   value(A) - value(subtract_list[weight(A)-d])
            thus there is a way to get a delta of d with a higher value, so subtract_list[s] can be ignored

        Case 2: 
            there does not exist any subset A of items from add_list[s+d] with:  w_max1 + d <= weight(A) < w_max1 + w_max2 + d

            In this case, there must exist a subset B of items from add_list[s+d] with
            w_max1 + w_max2 + d <= weight(B)
            and the cost of each item in B is less than the cost of max2

            To show this, we find B. Sort items of add_list[s+d] descending by weight, 
            and add items to B until w_max1 + w_max2 + d <= weight(B)

            All items within B must have weight > w_max2, otherwise B - final item added would invalidate the Case 2 assumption.
            Because max2 has weight higher than all previous items, all items in B must come later, and therefore have lower cost than max2.
            This means that:
                value(add_list[s+d]) - value(subtract_list[s])
            <=  value(B) + c_i*(s+d-weight(B)) - value(subtract_list[s])     because the items removed from add_list[s+d] have cost at most c_item
            <=  v_max1 + v_max2 + c_i*(s+d-w_max1-w_max2) - value(subtract_list[s])        because cost(B) <= c_max2 < c_i
            <=  v_max1 + v_max2 + c_i*(s+d-w_max1-w_max2) - c_i*(s+d-w_max1-w_max2) - value(subtract_list[w_max1+w_max2-d])     by the requirement I
            =   v_max1 + v_max2 - value(subtract_list[w_max1+w_max2-d]) 
            again, there is a way to get a higher value, so subtract_list[s] can be ignored.

        
        Great! Using just requirement I, we can ignore subtract_list[s]. So why do we need II and III?
        Well, I lets us ignore subtract_list[s] for the current item. But what about future items?
        And what about other sets we get by adding future elements to subtract_list[s]?
        Ideally, we could fully delete this row and never consider it again. This takes a little more rigor.

        First, what about future items? 
        Either subtract_list[s] is replaced by something with lower value, and would be deleted anyways,
        or requirement I still holds, since c_i and value(subtract_list[x]) will never increase
        But we run into an issue if we pass index max1. In this case the range of requirement I shifts.
        Requirement II ensures that subtract_list[s] will get replaced by this point, so we don't need to worry about this.

        Secondly, what about adding rows to subtract_list based on this one? Some subtract_list[s] + item_j
        Well, the value(subtract_list[s+w_j]) = value(subtract_list[s]) + c_j*w_j, so requirement I carries forward.
        And requirements II and III also carry forward as long as i < max1, by adding item_j to both lists in the inequalities.
        Because the new row inherits all requirements, it can also be disregarded. 

        The only remaining concern is adding a new item at index max1.
        subtract_list[s] + item_(max1-1) inherits the requirements, but it has 'slipped past' the max1 index, without being replaced due to requirement II.
        This is the case for which we need requirement III. 
            subtract_list[s] + item_max1
        >=  subtract_list[s-w_(max1-1)] + item_(max1_1) + item_max1     by requirement III

        
        So we will start at the end of subtract_list, removing items until we find one that does not meet all 3 requirements. Then move to the next item.
        Ideally the length of subtract_list never gets much longer than w_m1 + w_m2, but that depends on item_list.
        There may be a use case where this optimization needs further improvement, but for the sequences I'm working with, 
        the total runtime length is largely in generating item_list, which is due to checking huge primes,
        and there's not much I can do to speed that up. So I'll leave it here for now.

        """

        # check if we are going to hit max1, and handle if so
        if i + 1 == max1:
            max1 = max2
            max2 += 1
            while item_list[max1][1] > item_list[max2][1]:
                max2 += 1
                if max2 == len(item_list):
                    print('max2 reached end of item_list')
                    return sequence_list
                
            w_max1 = item_list[max1][1]
            w_max2 = item_list[max2][1] 
        
        # continue if subtract_list isn't large enough to delete from
        if len(subtract_list) <= w_max1 + w_max2:
            continue
        
        """
        instead of I)   value(subtract_list[s]) >= c_i * (s - x) + value(subtract_list[x]) 
        we use I)       value(subtract_list[s]) - c_i*s >= value(subtract_list[x]) - c_i*x 
        to split computation of s and x. We'll find the x with the highest value(subtract_list[x]) - c_i*x 
        and then use just that as a comparison for each s.
        """
        c_i_x = item_list[i+1][2]*w_max1
        max_x_value = direction*(subtract_list[w_max1][0] - c_i_x)
        for x in range(w_max1+1,w_max1+w_max2):
            c_i_x += item_list[i+1][2]
            max_x_value = max(max_x_value,direction*(subtract_list[x][0]-c_i_x))
        
        c_i_s = len(subtract_list)*item_list[i+1][2]
        for s in range(len(subtract_list)-1,w_max1+w_max2-1,-1):
            c_i_s -= item_list[i+1][2]

            requirement_I = (subtract_list[s][0] - c_i_s)*direction >= max_x_value
            requirement_II = subtract_list[s][0]*direction > direction*(subtract_list[s-w_max1][0] + item_list[max1][3])
            requirement_III = subtract_list[s][0]*direction > direction*(subtract_list[s-item_list[max1-1][1]][0] + item_list[max1-1][3])
            if requirement_I and requirement_II and requirement_III:
                subtract_list.pop()
            else:
                break


# this will convert the shorthand to explicit results of A379423 and A379424
# this assumes that the 'names' are meant to be multiplied, and will not work for the general application of infinite knapsack
def relative_to_explicit(relative_results,output_path,upper_limit = -1,type = ''):

    if upper_limit == -1:
        upper_limit = len(relative_results)

    explicit = [1]

    for r in range(1,upper_limit+1):
        explicit.append(explicit[relative_results[r][2]])
        c = 4
        div = False
        while c < len(relative_results[r]):
            if relative_results[r][c] == '-':
                div = True
            elif div:
                explicit[-1] = explicit[-1]//int(relative_results[r][c])
            else:
                explicit[-1] = explicit[-1]*int(relative_results[r][c])

            c += 1
    file_output([[x,explicit[x]] for x in range(len(explicit))],output_path,type)


def file_output(data_output, file_name, type = ''):
    with open(file_name,'w',encoding='utf-8') as f:
        for line in data_output:
            if type == 'b':
                f.write(' '.join([str(x) for x in line])+'\n')
            else:
                f.write(','.join([str(x) for x in line])+'\n')

def file_input(file_name,type=""):

    with open(file_name,encoding='utf-8',mode = 'r') as f:
        lines = f.readlines()
    data = [x.split(',') for x in lines]
    for row in data:
        if type == "relative":
            row[0] = int(row[0])
            row[1] = float(row[1])
            row[2] = int(row[2])
            row[-1] = row[-1].replace('\n','')
        else:
            row[0] = row[0]
            row[1] = int(row[1])
            row[2] = float(row[2])
            row[3] = float(row[3].replace('\n',''))
    return data



#start_time = time.time()

# A379423

item_list = file_input('A379423_factors.csv')
output_name = 'A379423_shorthand.csv'
out_list = infinite_knapsack_terms(item_list,output_name,-1)
file_output(out_list,output_name)
#out_list = file_input('A379423_shorthand.csv','relative')
relative_to_explicit(out_list,'A379423.csv',5000)
relative_to_explicit(out_list,'b379423.csv',1000,'b')


# A379424
"""
item_list = file_input('A379424_factors.csv')
output_name = 'A379424_shorthand.csv'
out_list = infinite_knapsack_terms(item_list,output_name,-1)
file_output(out_list,output_name)
#out_list = file_input('A379424_shorthand.csv','relative')
relative_to_explicit(out_list,'A379424.csv',1000)
relative_to_explicit(out_list,'b379424.csv',500,'b')
"""

#print(time.time()-start_time)