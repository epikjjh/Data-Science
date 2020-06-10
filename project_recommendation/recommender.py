import argparse


class Recommender:
    def __init__(self, args):
        # Save output file name
        self.output = args.training_file + "_prediction.txt"

        # Training data(User): {'user id': {'item id': rating ...} ...}
        # Training data(Item): {'item id': {'user id': rating ...} ...}
        # User average rating: {'user id': average value ...}
        # Item average rating: {'item id': average value ...}
        self.training_user = {}
        self.training_item = {}
        self.user_avg = {}
        self.item_avg = {}

        # Use user based only
        self.metric = 1

        with open(args.training_file, 'r') as f:
            for line in f.readlines():
                user_id, item_id, rating, _ = map(int,line.split())               
                # User
                if user_id not in self.training_user:
                    self.training_user[user_id] = {item_id: rating}
                else:    
                    self.training_user[user_id][item_id] = rating 
                
                # User avg rating
                if user_id not in self.user_avg:
                    self.user_avg[user_id] = [rating]
                else:
                    self.user_avg[user_id].append(rating)

                # In case of using item based
                if self.metric != 1:
                    # Item
                    if item_id not in self.training_item:
                        self.training_item[item_id] = {user_id: rating}
                    else:
                        self.training_item[item_id][user_id] = rating

                    # Item avg rating
                    if item_id not in self.item_avg:
                        self.item_avg[item_id] = [rating]
                    else:
                        self.item_avg[item_id].append(rating)

        # Process user average value
        for uid in self.user_avg.keys():
            self.user_avg[uid] = sum(self.user_avg[uid]) / len(self.user_avg[uid])

        # In case of using item based
        if self.metric != 1:
            # Process item average value
            for iid in self.item_avg.keys():
                self.item_avg[iid] = sum(self.item_avg[iid]) / len(self.item_avg[iid])

        # Test data: {'user id': {'item id': rating ...} ...}
        self.test = {}
        with open(args.test_file, 'r') as f:
            for line in f.readlines():
                user_id, item_id, _, _ = map(int,line.split())
                if user_id not in self.test:
                    self.test[user_id] = {item_id: 0}
                else:
                    self.test[user_id][item_id] = 0

        # Rating matrix(User): {'user id': {'user id': similarity ...} ...}
        self.user_matrix = {i: {j: 0.0 for j in self.training_user.keys()} for i in self.training_user.keys()}

        # In case of using item based
        if self.metric != 1:
            # Rating matrix(Item): {'item id': {'item id': similarity ...} ...}
            self.item_matrix = {i: {j: 0.0 for j in self.training_item.keys()} for i in self.training_item.keys()}

        # Get rating matrix(User) values
        self._get_user_matrix()

        # In case of using item based
        if self.metric != 1:
            # Get rating matrix(Item) values
            self._get_item_matrix()

        # Predict: weighted average
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


    def _get_pcc_similarity(self, v1, v2):
        ret = 0.0
        v1_size = 0.0
        v2_size = 0.0
        v1_mean = sum(v1) / len(v1)
        v2_mean = sum(v2) / len(v2)
        # Assume v1 has same length as v2
        for i in range(len(v1)):
            ret += (v1[i]-v1_mean)*(v2[i]-v2_mean)
            v1_size += (v1[i]-v1_mean)**2
            v2_size += (v2[i]-v2_mean)**2

        try:
            return ret / (v1_size**(1/2) * v2_size**(1/2))
        except ZeroDivisionError:
            return 0.0


    def _get_user_matrix(self):
        # Cosine similarity method
        # Set threshold: 0%
        threshold = len(self.training_user.keys()) * 0.0
        for i in self.training_user.keys():
            for j in self.training_user.keys():
                if i == j:
                    self.user_matrix[i][j] = 1.0
                else:
                    v1_dict = self.training_user[i]
                    v2_dict = self.training_user[j]
                    v1 = []
                    v2 = []
                    for iid in set(list(v1_dict.keys())+list(v2_dict.keys())):
                        if iid in v1_dict and iid in v2_dict:
                            v1.append(v1_dict[iid])
                            v2.append(v2_dict[iid])

                    # Avoid empty list
                    if v1 and v2:
                        if len(v1) >= threshold:
                            self.user_matrix[i][j] = self._get_cosine_similarity(v1,v2) 
                        else:
                            self.user_matrix[i][j] = 0.0


    def _get_item_matrix(self):
        # Cosine similarity method
        for i in self.training_item.keys():
            for j in self.training_item.keys():
                if i == j:
                    self.item_matrix[i][j] = 1.0
                else:
                    v1_dict = self.training_item[i]
                    v2_dict = self.training_item[j]
                    v1 = []
                    v2 = []
                    for uid in set(list(v1_dict.keys())+list(v2_dict.keys())):
                        if uid in v1_dict and uid in v2_dict:
                            v1.append(v1_dict[uid])
                            v2.append(v2_dict[uid])

                    # Avoid empty list
                    if v1 and v2:
                        self.item_matrix[i][j] = self._get_cosine_similarity(v1,v2) 


    def _get_rating_user(self, uid, iid):
        fraction = 0.0
        denominator = 0.0

        for user in self.user_matrix.keys():
            if iid in self.training_user[user]:
                fraction += self.user_matrix[uid][user] * (self.training_user[user][iid]-self.user_avg[user])
                denominator += self.user_matrix[uid][user]

        # Avoid divide by zero
        try:
            ret = self.user_avg[uid] + (fraction / denominator)
        except ZeroDivisionError:
            ret = self.user_avg[uid]

        ret = int(ret+0.5)
        # Clip value
        if ret > 5:
            ret = 5
        if ret < 1:
            ret = 1
        return ret
       
       
    def _get_rating_item(self, uid, iid):
        fraction = 0.0
        denominator = 0.0

        for item in self.item_matrix.keys():
            if item == iid:
                continue
            if uid in self.training_item[item] and iid in self.item_matrix[item]:
                fraction += self.item_matrix[item][iid] * (self.training_item[item][uid]-self.item_avg[item])
                denominator += self.item_matrix[iid][item]

        # Avoid divide by zero
        try:
            ret = self.item_avg[iid] + fraction / denominator
        except ZeroDivisionError:
        # Inject lowest value
            ret = self.item_avg[iid]

        ret = int(ret+0.5)
        # Clip value
        if ret > 5:
            ret = 5
        if ret < 1:
            ret = 1

        return ret


    def _predict(self):
        # User user based only
        for uid in self.test.keys():
            for iid in self.test[uid].keys():
                if self.metric != 1:
                    self.test[uid][iid] = self._get_rating_item(uid, iid)
                else:
                    self.test[uid][iid] = self._get_rating_user(uid, iid) 


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
