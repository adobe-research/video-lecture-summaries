#!/usr/bin/env python

import sklearn.cluster  as skcluster
import sklearn.metrics.pairwise as skpair
import numpy as np
from sklearn.preprocessing import StandardScaler

def affinity_propagation(n_points):
    ap = skcluster.AffinityPropagation(damping = .9)
    ap.fit(n_points)
    ap.predict(n_points)
    indices = ap.cluster_centers_indices_
    labels = ap.labels_
    return indices,labels

def spectral_clustering(n_points):
    pass

def dbscan(n_points):
    X = StandardScaler().fit_transform(n_points)
    mins = min(30, len(X))   
    db = skcluster.DBSCAN(min_samples = mins)
    db.fit(X)
    indices = db.core_sample_indices_
    labels = db.labels_
    return indices, labels



def similarity_matrix(n_points):
    D = skpair.euclidean_distances(n_points)
    S = 1./D    
    return S
