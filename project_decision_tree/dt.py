import sys
from math import log
import pandas as pd

class TreeNode:
    def __init__(self, df):
        self.df = df



class DecisionTree:
    def __init__(self, df):
        self.df = df
        self.label = df.columns[-1]
        self._calculate_entropy(self.df)
        self._calculate_information_gain(self.df, 'age')


    # Calculate Info(D) when D is given (D denotes data set)
    # Info(D) = -sigma[p(i)*log2(p(i))] 1 to m (m denotes number of class labels)
    # Order?: Doesn't matter
    # !!! should consider data set dimension!!!
    def _calculate_entropy(self, data_set):
        total = len(data_set)
        ret = 0.0
        for _,val in data_set[self.label].value_counts().iteritems():
            p_val = val/total
            ret += -p_val*log(p_val,2)
        return ret
        
    
    # Calculate Information Gain
    # Calculate InfoA(D) when D and attribute are given (D denotes data set)
    # InfoA(D) = sigma[|D(j)|/|D|*Info(D(j)] (|D| denotes size of data set)
    # !!!sholud consider data set dimension!!!
    def _calculate_information_gain(self, data_set, attribute):
        ret = 0.0
        total = len(data_set)
        info_D = self._calculate_entropy(data_set)
        for atype,_ in data_set[attribute].value_counts().iteritems():
            df_filtered = data_set[data_set[attribute]==atype]
            info_att = self._calculate_entropy(df_filtered)
            ret += info_att*(len(df_filtered)/total)

        return info_D - ret


    # Select best attribute
    def _select_attribute(self):
        


    #def _build_node(self):



    #def _calculate_gain_ratio(self):

    #def _calculate_gini_index(self):



if __name__ == "__main__":
    train_file, test_file, output_file = sys.argv[1:]
    df_train = pd.read_csv(train_file, sep="\t")
    df_test = pd.read_csv(test_file, sep="\t")
    dt = DecisionTree(df_train)
