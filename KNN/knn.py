import numpy as np

class KNN:

    def __init__(self, task:str, k=3):
        
        assert task in ('classification', 'regression')
        assert k >= 1

        self.task = task
        self.k = k
    
    def fit(self, X, y):

        assert type(X) == np.ndarray
        assert len(X.shape) == 2

        assert type(y) == np.ndarray
        assert len(y.shape) == 1

        assert X.shape[0] == y.shape[0]

        self.X = X
        self.y = y
    
    def predict(self, samples):
        nearest_points_indexes = np.zeros((len(samples), self.k), dtype='int64')

        distances = np.zeros((len(samples), len(self.X)))

        labels = np.full((len(samples),), fill_value=np.inf)

        # compute distances
        for i in range(len(samples)):

            distances[i] = self.__distance(samples[i], self.X)
        
        # find k nearest points
        for i in range(len(samples)):

            for j in range(self.k):

                close_point_index = distances[i].argmin()

                nearest_points_indexes[i][j] = close_point_index

                distances[i][close_point_index] = np.inf
        
        if self.task == 'classification':

            for i in range(len(samples)):

                values = np.full((self.k), fill_value=np.inf)

                for j in range(self.k):

                    values[j] = self.y[nearest_points_indexes[i][j].item()]
                
                labels[i] = self.__most_frequent(values)

            return labels

        # regression
        for i in range(len(samples)):
            values = np.full((self.k,), fill_value=np.inf)

            for j in range(self.k):

                values[j] = self.y[nearest_points_indexes[i][j].item()]

            labels[i] = values.mean()

        return labels

    
    def __call__(self, X):
        return self.predict(X)
    
    def __distance(self, a, b):
        distances = np.zeros((len(b)))

        for i in range(len(b)):
            if a.shape == b.shape:
                distances[i] = np.sqrt(np.sum(
                        (a[i] - b[i])**2,
                        axis=0
                ))
            else:
                distances[i] = np.sqrt(np.sum(
                        (a - b[i])**2,
                        axis=0
                ))
        return distances
    
    def __most_frequent(self, array):
        return np.max(array)