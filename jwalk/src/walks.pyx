# -*- coding: utf-8 -*-
"""Perform random walks on sparse csr matrix."""
from libc.stdlib cimport rand, RAND_MAX

import cython
cimport numpy as np
import numpy as np


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cdef Py_ssize_t _choose_one(double [:] pmf) nogil:
    """Random choice with discrete probabilities.

    Args:
        pmf (double[:]): probability mass function
    """
    cdef:
        Py_ssize_t i, length
        double random, total

    random = rand() / (RAND_MAX + 1.0)
    length = pmf.shape[0]
    i = 0
    total = 0.0

    while total < random and i < length:
        total += pmf[i]
        i += 1
    return i - 1


@cython.profile(False)
@cython.boundscheck(False)
@cython.wraparound(False)
def walk_random(normalized_csr, np.ndarray labels, int walk_length):
    """Generate random walks for each node in a normalized sparse csr matrix.

    Args:
        normalized_csr (scipy.sparse.csr_matrix): normalized adjacency matrix
        labels (np.ndarray): array of node labels
        walk_length (int): length of walk

    Returns:
        np.array walks, np.array word frequencies
    """
    cdef:
        int [:] indices = normalized_csr.indices
        int [:] indptr = normalized_csr.indptr
        double [:] data = normalized_csr.data
        int num_nodes = normalized_csr.shape[0]
        long [:] vocab_cnt = np.ones(num_nodes, dtype=int)

        int [:] neighbors
        double [:] weights
        int i, j, node_index, weight_index, next_index

    walks = np.empty([num_nodes, walk_length], dtype=object)
    walks.fill('')
    walks.T[0] = labels

    for i in range(num_nodes):
        node_index = i
        for j in range(walk_length-1):
            neighbors = indices[indptr[node_index]:indptr[node_index+1]]
            if neighbors.shape[0] == 0:  # stop walk
                break
            weights = data[indptr[node_index]:indptr[node_index+1]]
            weight_index = _choose_one(weights)
            next_index = neighbors[weight_index]
            walks[i][j+1] = labels[next_index]
            vocab_cnt[next_index] += 1
            node_index = next_index

    return walks, np.asarray(vocab_cnt)
