import sys

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


def generate(vcand,length):
    ncand = [vcand[i].union(vcand[j]) for i in range(len(vcand)) for j in range(i+1,len(vcand))]
    ncand = list(set(tuple(sorted(elem)) for elem in ncand))
    ncand = list(filter(lambda x: len(x)==length, ncand)) 
    ncand = list(map(set,ncand))
    return ncand


if __name__ == "__main__":
    # Command line argument
    min_sup, input_file, output_file = sys.argv[1:]
    min_sup = float(min_sup)
    f = open(input_file, 'r')
    # Create transaction table
    table = {tid: set(map(int,line.split())) for tid,line in enumerate(f.readlines())}
    f.close()
    # Create candidates: length 1
    items = {value for row in table.values() for value in row} 
    cand = [[{item} for item in items]]
    v_list = [verify(cand[0])]
    max_length = 1
    while True:
        cand.append(generate(v_list[-1],max_length+1))
        vcand = verify(cand[-1])
        if not vcand:
            break
        v_list.append(vcand)
        max_length += 1
    print(max_length)
    print(v_list)
