import argparse

class Cluster:
    def __init__(self, args):
        # Initialize values
        self.input_file = args.input_file
        self.n = args.n
        self.eps = args.eps
        self.minpts = args.minpts
        
        # Save output file names
        title = self.input_file.split('.')[0] 
        self.output_file = [title+"_cluster_{}.txt".format(i) for i in range(self.n)]

        # Extract data
        with open(self.input_file, 'r') as f:
            data = [line.split() for line in f.readlines()]
            self.data = {int(e[0]): (float(e[1]), float(e[2])) for e in data}

        # Get each data's neighbors & corepoints
        self._get_neighbors()
        self._get_corepoints()

        # Set visited array
        self.visited = []
        # Get clusters()
        self._get_clusters()

        # Write result 
        self._write_result()



    @staticmethod
    def _get_distance(x1, y1, x2, y2):
        return ((x1-x2)**2 + (y1-y2)**2)**(1/2)


    def _get_neighbors(self):
        self.neighbors = {key: [] for key in self.data.keys()}
        for e1_key, (e1_x, e1_y) in self.data.items():
            for e2_key, (e2_x, e2_y) in self.data.items():
                if e1_key == e2_key:
                    continue
                dist = self._get_distance(e1_x, e1_y, e2_x, e2_y)
                if dist <= self.eps:
                    self.neighbors[e1_key].append(e2_key)


    def _get_corepoints(self):
        self.core_pts = [key for key, val in self.neighbors.items() if len(val) >= self.minpts]

        
    def _get_clusters(self):
        self.clusters = []
        # Visit core points first
        # BFS
        for cpt in self.core_pts:
            if cpt in self.visited:
                continue
            queue = [cpt]
            cluster = [cpt]
            self.visited.append(cpt)
            while len(queue)>0:
                cur = queue.pop(0)
                for nxt in self.neighbors[cur]:
                    if nxt not in self.visited:
                        self.visited.append(nxt)
                        cluster.append(nxt)
                        if nxt in self.core_pts:
                            queue.append(nxt)

            self.clusters.append(cluster)

        # Sort clusters
        self.clusters = sorted(self.clusters, key=lambda x: len(x), reverse=True)
        # Select n clusters
        self.clusters = self.clusters[:self.n]


    def _write_result(self):
        for i, file_name in enumerate(self.output_file):
            with open(file_name, 'w') as f:
                for e in self.clusters[i]:
                    f.write("{}\n".format(e))
        

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)
    parser.add_argument("n", type=int)
    parser.add_argument("eps", type=int)
    parser.add_argument("minpts", type=int)
    args = parser.parse_args()

    # Create cluster object
    dbscan = Cluster(args)
