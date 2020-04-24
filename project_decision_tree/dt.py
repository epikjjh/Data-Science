import sys
from math import log
import pandas as pd

class TreeNode:
    def __init__(self, attribute, isleaf=False, metric=None):
        self.attribute = attribute
        self.child = {}
        self.isleaf = isleaf
        self.metric = metric


class DecisionTree:
    def __init__(self, df):
        self.label = df.columns[-1]
        self.root =  self._build_tree(df)


    # Calculate Info(D) when D is given (D denotes data set)
    # Info(D) = -sigma[p(i)*log2(p(i))] 1 to m (m denotes number of class labels)
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
    def _calculate_information_gain(self, data_set, attribute):
        ret = 0.0
        info_D = self._calculate_entropy(data_set)
        for atype,_ in data_set[attribute].value_counts().iteritems():
            df_filtered = data_set[data_set[attribute]==atype]
            info_att = self._calculate_entropy(df_filtered)
            ret += info_att*(len(df_filtered)/len(data_set))

        return info_D - ret


    # Select best attribute
    def _select_attribute(self, data_set):
        att_dict = {attribute: self._calculate_information_gain(data_set,attribute) for attribute in data_set.columns if attribute!=self.label}
        # Sort dictionary by key: descending -> tuple(attribute, information gain)
        return sorted(att_dict.items(),key=lambda x: x[1], reverse=True)[0][0]


    # Build node by using selected attribute
    def _build_node(self, data_set):
        target_att = self._select_attribute(data_set)
        return TreeNode(target_att)


    # Build tree
    # Exception????
    def _build_tree(self, data_set):
        # Data is classified perfectly
        if data_set[self.label].nunique() == 1:
            uval = data_set[self.label].unique()[0]
            return TreeNode(None,True,uval)

        # There are no remaining attributes -> majority voting
        elif len(data_set.columns) == 1:
            #!!!Need to implement majority voting!!!
            major = data_set[self.label].unique()[0]
            return TreeNode(None,True,major)

        # Build node
        node = self._build_node(data_set)

        # Split data set
        for atype,_ in data_set[node.attribute].value_counts().iteritems():
            df_filtered = data_set[data_set[node.attribute]==atype].drop(node.attribute, axis=1)
            # Exception????
            if len(df_filtered) > 0:
                node.child[atype] = self._build_tree(df_filtered)

        return node


    # Tree traversal
    def _traverse_tree(self, tuple_data):
        node = self.root
        atype = tuple_data[node.attribute]
        while not node.isleaf:
            node = node.child[atype]
            if node.attribute:
                atype = tuple_data[node.attribute]

        return node.metric


    # output
    def output(self, data_set):
        #label = [self._traverse_tree(data_set.loc[idx]) for idx in range(len(data_set))]
        label = []
        for idx in range(len(data_set)):
            try:
                label.append(self._traverse_tree(data_set.loc[idx]))
            except:
                print(data_set.loc[idx])
                label.append("Error")
        data_set[self.label] = label
        return data_set
        

    #def _calculate_gain_ratio(self):

    #def _calculate_gini_index(self):



if __name__ == "__main__":
    train_file, test_file, output_file = sys.argv[1:]
    df_train = pd.read_csv(train_file, sep="\t")
    df_test = pd.read_csv(test_file, sep="\t")
    dt = DecisionTree(df_train)
    
    ret = dt.output(df_test)
    ret.to_csv(output_file, sep="\t")
