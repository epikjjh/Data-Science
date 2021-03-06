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
    def __init__(self, df, metric_type):
        self.metric_type = metric_type
        self.label = df.columns[-1]
        self.attribute_dict = {attribute: df[attribute].unique() for attribute in df.columns if attribute!=self.label}
        self.root =  self._build_tree(df)


    # Calculate Info(D) when D is given (D denotes data set)
    # Info(D) = -sigma[p(i)*log2(p(i))] 1 to m (m denotes number of class labels)
    def _calculate_entropy(self, data_set):
        total = len(data_set)
        ret = 0.0
        for _,val in data_set[self.label].value_counts().iteritems():
            p_val = val/total
            # Avoid log2(0)
            ret += -p_val*log(p_val+1e-7,2)
        return ret
        
    
    # Calculate Information Gain
    # Calculate InfoA(D) when D and attribute are given (D denotes data set)
    # InfoA(D) = sigma[|D(j)|/|D|*Info(D(j)] (|D| denotes size of data set)
    def _calculate_information_gain(self, data_set, attribute):
        ret = 0.0
        info_D = self._calculate_entropy(data_set)
        for atype in self.attribute_dict[attribute]:
            df_filtered = data_set[data_set[attribute]==atype]
            info_att = self._calculate_entropy(df_filtered)
            ret += info_att*(len(df_filtered)/len(data_set))

        return info_D - ret


    # Calculate split info
    # SplitInfoA(D) = -sigma[|D(j)|/|D|*log2(|D(j)|/|D|)] (|D| denotes size of data set)
    def _calculate_split_info(self, data_set, attribute):
        ret = 0.0
        for atype in self.attribute_dict[attribute]:
            df_filtered = data_set[data_set[attribute]==atype]
            partial = len(df_filtered)/len(data_set)
            log_val = log(partial+1e-7,2)
            # Avoid log2(0)
            ret += -1.0*(partial*log_val)

        return ret
        
        
    # Calculate Gain Ratio
    # GainRatio(A) = Gain(A) / SplitInfo(A)
    def _calculate_gain_ratio(self, data_set, attribute):
        gain = self._calculate_information_gain(data_set,attribute)
        split_info = self._calculate_split_info(data_set,attribute)

        return gain/split_info


    # Calculate Gini(D)
    def _calculate_gini(self, data_set):
        ret = 1.0
        total = len(data_set)
        for _,val in data_set[self.label].value_counts().iteritems():
            partial = val/total
            ret -= partial**2

        return ret


    # Calculate GiniA(D)
    def _calculate_gini_index(self, data_set, attribute, left, right):
        total = len(data_set)
        # Left
        df_left = data_set[data_set[attribute].isin(left)]
        left_scale = len(df_left)/total
        left_gini = self._calculate_gini(df_left)
        # Right
        df_right = data_set[data_set[attribute].isin(right)]
        right_scale = len(df_right)/total
        right_gini = self._calculate_gini(df_right)

        return left_scale*left_gini + right_scale*right_gini 


    def _choose_branch(self, data_set, attribute):
        atypes = self.attribute_dict[attribute]
        gini_dict = {}
        for i in range(1,len(atypes)):
            left = tuple(atypes[:i])
            right = tuple(atypes[i:])
            gini_dict[(left,right)] = self._calculate_gini_index(data_set, attribute, left, right)
        # Sort dictionary by value: ascending -> tuple((left,right), gini index)
        return sorted(gini_dict.items(),key=lambda x: x[1], reverse=False)[0][0]


    def _majority_vote(self, data_set):
        major = df_train[self.label].value_counts().sort_values(ascending=False)
        return major.index[0]


    # Select best attribute
    def _select_attribute(self, data_set):
        # Type 0: Use information gain
        if self.metric_type == 0:
            info_dict = {attribute: self._calculate_information_gain(data_set,attribute) for attribute in data_set.columns if attribute!=self.label}
            # Sort dictionary by value: descending -> tuple(attribute, information gain)
            return sorted(info_dict.items(),key=lambda x: x[1], reverse=True)[0][0]

        # Type 1: Use gain ratio 
        elif self.metric_type == 1:
            ratio_dict = {attribute: self._calculate_gain_ratio(data_set,attribute) for attribute in data_set.columns if attribute!=self.label}
            # Sort dictionary by value: descending -> tuple(attribute, gain ratio) 
            return  sorted(ratio_dict.items(),key=lambda x: x[1], reverse=True)[0][0]


    # Build node by using selected attribute
    def _build_node(self, data_set):
        target_att = self._select_attribute(data_set)
        return TreeNode(target_att)

    
    # Build tree
    def _build_tree(self, data_set):
        # Data is classified perfectly
        if data_set[self.label].nunique() == 1:
            uval = data_set[self.label].unique()[0]
            return TreeNode(None,True,uval)

        # There are no remaining attributes -> majority voting
        elif len(data_set.columns) == 1:
            # majority voting
            major = self._majority_vote(data_set)
            return TreeNode(None,True,major)

        # Build node & choose attribute
        node = self._build_node(data_set)
        # For post pruning
        node.metric = self._majority_vote(data_set) 
        # Choose proper branch by using gini index -> binary tree
        for branch in self._choose_branch(data_set, node.attribute):
            #df_filtered = data_set[data_set[node.attribute].isin(branch)].drop(node.attribute, axis=1)
            df_filtered = data_set[data_set[node.attribute].isin(branch)]
            if len(df_filtered) > 0:
                node.child[tuple(branch)] = self._build_tree(df_filtered)
            # There are no remaining tuples -> majority voting
            else:
                major = self._majority_vote(data_set)
                node.child[tuple(branch)] = TreeNode(None,True,major) 
        return node


    # Tree traversal
    def _traverse_tree(self, tuple_data):
        node = self.root
        atype = tuple_data[node.attribute]
        while not node.isleaf:
            # Select branch
            for branch, nxt_node in node.child.items():
                if atype in branch:
                    break
            node = nxt_node
            if node.attribute:
                atype = tuple_data[node.attribute]

        return node.metric


    # output
    def output(self, data_set):
        label = [self._traverse_tree(data_set.loc[idx]) for idx in range(len(data_set))]
        data_set[self.label] = label
        return data_set


if __name__ == "__main__":
    train_file, test_file, output_file = sys.argv[1:]
    df_train = pd.read_csv(train_file, sep="\t")
    df_test = pd.read_csv(test_file, sep="\t")
    # Attribute selection: information gain
    # Branch selection: gini index
    dt = DecisionTree(df_train,0)
    
    ret = dt.output(df_test)
    ret.to_csv(output_file, sep="\t")
