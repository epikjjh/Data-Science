import sys
from itertools import combinations

def verify(cand):
    # Convert set to list for indexing
    #cand = list(map(list,cand))
    c_table = {idx: 0 for idx, _ in enumerate(cand)}
    for row in table.values():
        for idx,elem in enumerate(cand):
            flag = True
            for e in elem:
                if e not in row:
                    flag = False
                    break
            if(flag):
                c_table[idx] += 1
    ret_idx = [idx for idx, val in c_table.items() if val>=min_sup]
    ret_set = [cand[idx] for idx in ret_idx]

    return ret_set        


def generate_freq_list(vcand,length):
    ncand = [vcand[i].union(vcand[j]) for i in range(len(vcand)) for j in range(i+1,len(vcand))]
    ncand = list(set(tuple(sorted(elem)) for elem in ncand))
    ncand = list(filter(lambda x: len(x)==length, ncand)) 
    ncand = list(map(set,ncand))
    return ncand


def generate_association_rule(freq_list):
    ret = []
    for elem in freq_list:
        set_length = len(elem[0])
        if set_length <= 1:
            continue
        for e in elem:
            for l in range(1,set_length):
                total_combinations = combinations(e,l)       
                for combination in total_combinations:
                    left = set(combination)
                    right = e - left
                    total_cnt=0; left_cnt=0
                    for data in table.values():
                        if data >= e:
                            total_cnt += 1
                        if data >= left:
                            left_cnt += 1
                    sup = float(total_cnt)/len(table)*100
                    conf = float(total_cnt)/left_cnt*100
                    ret.append("{}\t{}\t{:.2f}\t{:.2f}\n".format(str(left),str(right),sup,conf))
    return ret


if __name__ == "__main__":
    # Command line argument
    min_sup, input_file, output_file = sys.argv[1:]
    min_sup = float(min_sup)/100
    # Create transaction table
    with open(input_file, 'r') as f:
        table = {tid: set(map(int,line.split())) for tid,line in enumerate(f.readlines())}
    # Convert ratio to count
    min_sup = len(table)*min_sup
    # Create candidates: length 1
    items = {value for row in table.values() for value in row} 
    cand = [[{item} for item in items]]
    freq_list = [verify(cand[0])]
    max_length = 1
    while True:
        cand.append(generate_freq_list(freq_list[-1],max_length+1))
        vcand = verify(cand[-1])
        if not vcand:
            break
        freq_list.append(vcand)
        max_length += 1
    association_list = generate_association_rule(freq_list)
    with open(output_file, 'w') as f:
        for line in association_list:
            f.write(line)
