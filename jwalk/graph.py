# -*- coding: utf-8 -*-
"""Build encoded sparse csr matrix."""
import logging

import numpy as np
import scipy.sparse as sps

__all__ = ['build_adjacency_matrix', 'encode_edges']

logger = logging.getLogger(__name__)


def encode_edges(edges, nodes):
    """Encode data with dictionary

    Args:
        edges (np.ndarray): np array of the form [node1, node2].
        nodes (np.array): list of unique nodes

    Returns:
        np.ndarray: relabeled edges

    Examples:
        >>> import numpy as np
        >>> edges = np.array([['A', 'B'], ['A', 'C']])
        >>> nodes = np.array(['C', 'B', 'A'])
        >>> print(encode_edges(edges, nodes))
        [[2 1]
         [2 0]]
    """
    sidx = nodes.argsort()
    relabeled_edges = sidx[np.searchsorted(nodes, edges, sorter=sidx)]
    return relabeled_edges


def build_adjacency_matrix(edges, undirected=False):
    """Build adjacency matrix.

    Args:
        edges (np.ndarray): a 2 or 3 dim array of the form [src, tgt, [weight]]
        undirected (bool): if True, add matrix with its transpose

    Returns:
        scipy.sparse.csr_matrix: adjacency matrix, np.ndarray: labels
    """
    assert edges.shape[1] in [2, 3], "Input must contain 2 or 3 columns"

    if edges.shape[1] == 2:  # if no weights
        logger.info("Weight column not found. Defaulting to value 1.")
        weights = np.ones(edges.shape[0], dtype='float')
    else:
        weights = edges[:, 2].astype('float')

    edges = edges[:, :2]
    nodes = np.unique(edges)  # returns sorted
    num_nodes = nodes.shape[0]

    encoded = encode_edges(edges, nodes)

    sp = sps.csr_matrix((weights, encoded.T), shape=(num_nodes, num_nodes))

    if undirected:
        sp = make_undirected(sp)
    return sp, nodes


def make_undirected(csr_matrix):
    """Make CSR matrix undirected."""
    return csr_matrix + csr_matrix.T
