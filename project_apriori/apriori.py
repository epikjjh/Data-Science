import sys
from itertools import combinations

'''
    Feature: Prune candidates by support and length
    Arguments: cand(type: list[set])
    Return value type: dictionary(key: tuple, value: float]
'''
def prune(cand):
    # Make counting table
    cnt_table = {idx: 0 for idx, _ in enumerate(cand)}
    for transaction in table:
        for idx,itemset in enumerate(cand):
            # Check whether each transaction is superset of each itemset
            if transaction >= itemset:
                cnt_table[idx] += 1
    # Filter by minimum support
    ret = {tuple(cand[key]): val/len(table)*100 for key, val in cnt_table.items() if val>=min_sup}

    return ret        


'''
    Feature: Generate candidates by self-joining
    Arguments: itemdict(type: dictionary(key: tuple, value: float)), length(type: integer)
    Return value type: list[set]
'''
def self_join(itemdict,length):
    # Convert type: tuple->set
    itemsets = list(map(set,itemdict.keys()))
    # Generate candidates by set union operator
    ret = [itemsets[i]|itemsets[j] for i in range(len(itemsets)) for j in range(i+1,len(itemsets))]
    # Filter by length
    ret = list(filter(lambda x: len(x)==length, ret)) 
    # Remove duplicates
    ret = list(set(tuple(sorted(itemset)) for itemset in ret))
    # Convert type: tuple->set 
    ret = list(map(set,ret))
    return ret


'''
    Feature: Gerneate association rules
    Arguments: freq_list(type: list[dictionary(key: tuple. value: float)])
    Return value type: list[string] 
'''
def generate_association_rule(freq_list):
    ret = []
    for itemdict in freq_list:
        for itemset,val in itemdict.items():
            # Exception: length is less or equal than 1
            if len(itemset) <= 1:
                break
            # Save support value
            sup = val
            # Convert type: tuple->set 
            itemset = set(itemset)
            for length in range(1,len(itemset)):
                # Generate all combinations
                total_combinations = combinations(itemset,length)       
                for combination in total_combinations:
                    # Convert type: tuple->set 
                    left = set(combination)
                    right = itemset - left
                    left_cnt=0
                    for transaction in table:
                        if transaction >= left:
                            left_cnt += 1
                    # Calculate confidence
                    conf = sup*len(table)/left_cnt
                    # Save result as string
                    ret.append("{}\t{}\t{:.2f}\t{:.2f}\n".format(str(left),str(right),sup,conf))
    return ret


if __name__ == "__main__":
    '''
        Initialize arguments
        [Type]
            min_sup: float(ratio)->integer(count)
            input_file: string
            output_file: string
    '''
    # Save command line argument
    min_sup, input_file, output_file = sys.argv[1:]
    # Convert type: string->float
    min_sup = float(min_sup)/100

    ''' 
        Read input file
        & Create transaction table
        [Type]
            table: list[sorted sets]
    '''
    with open(input_file, 'r') as f:
        table = [set(sorted(map(int,line.split()))) for line in f.readlines()]

    # Convert: ratio->count
    min_sup = len(table)*min_sup

    '''
        Generate candidates(Self-joining)
        & Prune candidates
        => Generate frequent item sets depending on its length
        [Type]
            itmes: set
            cand_list: list[list[set]] 
            freq_list: list[dictionary(key:tuple, value=float(support))]
            max_length: integer
    '''
    # Create candidates: length 1
    items = {item_id for transaction in table for item_id in transaction} 
    cand_list = [[{item_id} for item_id in items]]
    freq_list = [prune(cand_list[0])]
    max_length = 1
    # Create candidates depending on its length
    while True:
        cand_list.append(self_join(freq_list[-1],max_length+1))
        tmp = prune(cand_list[-1])
        if not tmp:
            break
        freq_list.append(tmp)
        max_length += 1

    '''
        Generate association rules
        [Type]
            association_list: list[string]
    '''
    association_list = generate_association_rule(freq_list)
    # Write results in output file 
    with open(output_file, 'w') as f:
        for line in association_list:
            f.write(line)
