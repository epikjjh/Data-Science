import argparse


class Recommender:
    def __init__(self, args):
        # Save output file name
        self.output = args.training_file + "_prediction.txt"

        # Training data: {'user id': {'item id': rating ...} ...}
        self.training = {}
        with open(args.training_file, 'r') as f:
            for line in f.readlines():
                user_id, item_id, rating, _ = map(int,line.split())               
                if user_id not in self.training:
                    self.training[user_id] = {item_id: rating}
                else:    
                    self.training[user_id][item_id] = rating 
        
        # Test data: {'user id': {'item id': rating ...} ...}
        self.test = {}
        with open(args.test_file, 'r') as f:
            for line in f.readlines():
                user_id, item_id, _, _ = map(int,line.split())
                if user_id not in self.test:
                    self.test[user_id] = {item_id: 0}
                else:
                    self.test[user_id][item_id] = 0

        # Rating matrix: {'user id': {'user id': similarity ...} ...}
        self.rating_matrix = {i: {j: 0.0 for j in self.training.keys()} for i in self.training.keys()}
        # Get rating matrix values
        self._get_rating_matrix()

        # Predict: User-Based method -> weighted average
        self._predict()

        # Save prediction data 
        self._write()


    def _get_cosine_similarity(self, v1, v2):
        ret = 0.0
        v1_size = 0.0
        v2_size = 0.0
        # Assume v1 has same length as v2
        for i in range(len(v1)):
            ret += v1[i]*v2[i]
            v1_size += v1[i]**2
            v2_size += v2[i]**2

        return ret / (v1_size**(1/2) * v2_size**(1/2))


    def _get_rating_matrix(self):
        # Cosine similarity method
        for i in self.training.keys():
            for j in self.training.keys():
                if i == j:
                    self.rating_matrix[i][j] = 1.0
                else:
                    v1_dict = self.training[i]
                    v2_dict = self.training[j]
                    v1 = []
                    v2 = []
                    for iid in set(list(v1_dict.keys())+list(v2_dict.keys())):
                        if iid in v1_dict and iid in v2_dict:
                            v1.append(v1_dict[iid])
                            v2.append(v2_dict[iid])

                    # Avoid empty list
                    if v1 and v2:
                        self.rating_matrix[i][j] = self._get_cosine_similarity(v1,v2) 

    
    def _get_rating_value(self, uid, iid):
        fraction = 0.0
        denominator = 0.0

        for user in self.rating_matrix.keys():
            if user == uid:
                continue
            if iid in self.training[user]:
                fraction += self.rating_matrix[uid][user] * self.training[user][iid]
                denominator += self.rating_matrix[uid][user]

        # Avoid divide by zero
        if fraction == 0.0:
            # Inject lowest value
            ret = 1 
        else:
            ret = fraction / denominator

        return int(ret+0.5)


    def _predict(self):
        for uid in self.test.keys():
            for iid in self.test[uid].keys():
                self.test[uid][iid] = self._get_rating_value(uid, iid) 


    def _write(self):
        with open(self.output, 'w') as f:
            for uid in self.test.keys():
                for iid in self.test[uid]:
                    f.write("{}\t{}\t{}\n".format(uid,iid,self.test[uid][iid]))


        

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("training_file", type=str)
    parser.add_argument("test_file", type=str)
    args = parser.parse_args()
    recommender = Recommender(args)
