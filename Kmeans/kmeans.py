import numpy as np

class KMeans:
    
  def __init__(self, K, max_iters):
    self.K = K
    self.max_iters = max_iters

    self.centroids = []
    self.clusters = []

    self.associtations = [[] for _ in range(K)]

  def fit(self, X:np.ndarray):
    history = dict()

    self.n_features = X.shape[1]
    self.n_samples = X.shape[0]
    self._init_clusters(X)

    for epoch in range(self.max_iters):

      history[str(epoch)] = self.clusters

      # find distances from each data point to the cluster mean
      for i in range(len(self.clusters)):
        self.centroids.append([])

        for j in range(len(X)):
          self.centroids[i].append(self._distance(self.clusters[i], X[j]))

      # apply transfrom so it is more convinent to work with array
      nd_centroids = np.array(self.centroids).T
      # find the closest cluster to the cluster
      associeated_indicies = np.argmin(nd_centroids, axis=-1)

      # associeated_indicies[i] will return the closest cluster index
      # we append the sample to that cluster
      for i in range(self.n_samples):
        self.associtations[associeated_indicies[i]].append(X[i].tolist())

      # find the mean of the cluster's data point
      # means = np.array(self.associtations).mean(axis=1)
      means = [[] for i in range(self.K)]

      for i in range(self.K):
        for j in range(self.n_features):
          result = 0
          for z in range(len(self.associtations[i])):
            result += self.associtations[i][z][j]
          if len(self.associtations[i]) != 0:
            result /= len(self.associtations[i])
          means[i].append(result)
      # apply means of cluster's data point to the clusters
      result = self._update_clusters(means)

      # empty the data
      self.associtations = [[] for _ in range(self.K)]
      self.centroids = []

      # if result is not none, this means that there isn't much changes in cluster. so we break the training
      if result != None:
        break

    return history

  def predict(self, data_points:np.ndarray):
    return self(data_points)

  def __call__(self, data_points:np.ndarray):
    assert data_points.shape[1] == self.n_features

    results = []
    for i in range(len(data_points.tolist())):
      distances = []
      for k in range(self.K):
        distances.append(self._distance(self.clusters[k], data_points[i]))

      results.append(np.argmin(distances))

    return results

  def _update_clusters(self, values):
    if np.all((np.array(values) - np.array(self.clusters)) == 0):
      return -1

    self.clusters = values
    return None

  def _init_clusters(self, X:np.ndarray):

    for n in range(self.K):
      cluster_coords = []

      for i in range(self.n_features):
        cluster_coords.append(np.random.uniform(np.min(X[:, i]), np.max(X[:, i])))

      self.clusters.append(cluster_coords)

  def _distance(self, p1, p2):
    return np.sqrt(sum((x2-x1)**2 for x2,x1 in zip(p1, p2)))