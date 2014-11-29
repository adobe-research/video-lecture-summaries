'''
Created on Oct 22, 2014

@author: hijungshin
'''

import numpy as np
from sklearn.cluster import MeanShift, estimate_bandwidth
import matplotlib.pyplot as plt
from itertools import cycle
from sklearn.datasets.samples_generator import make_blobs


def plot(data, labels, cluster_centers):
    labels_unique = np.unique(labels)
    n_clusters = len(labels_unique)
    print "Estimated number of clusters: %d" % n_clusters
    plt.figure(1)
    plt.clf()    
    colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
    for k, col in zip(range(n_clusters), colors):
        my_members = labels == k
        cluster_center = cluster_centers[k]
        plt.plot(data[my_members, 0], data[my_members, 1], col + '.')
        plt.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
                 markeredgecolor='k', markersize=14)
    plt.title('Estimated number of clusters: %d' % n_clusters)
    return plt

def write(labels, outfile):
    txtfile = open(outfile, "w")
    for l in labels:
        txtfile.write("%i\n" % int(l))
    txtfile.close()

def cluster(data, bandwidth):
    ms = MeanShift(bandwidth=bandwidth)
    ms.fit(data)
    labels = ms.labels_
    cluster_centers = ms.cluster_centers_
    
    return labels, cluster_centers

def cluster_with_seeds(data, seeds):
    ms = MeanShift(seeds=seeds)
    ms.fit(data)
    labels = ms.labels_
    cluster_centers = ms.cluster_centers_
    return labels, cluster_centers

if __name__ == "__main__":
    X = [(0,1), (0,3), (0,2.5), (0,33), (0,2.6), (0,30), (2,10)]
    print X
    mydata = np.array(X)
    print mydata
    cluster(mydata)