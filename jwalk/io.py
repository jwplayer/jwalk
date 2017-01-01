# -*- coding: utf-8 -*-
"""Load and save data."""
import logging

import numpy as np
import scipy.sparse as sps

try:
    import pandas as pd
except ImportError:
    PANDAS_INSTALLED = False
else:
    PANDAS_INSTALLED = True

__all__ = ['load_edges', 'load_graph', 'save_graph']

logger = logging.getLogger(__name__)


def load_edges(fpath, delimiter=None, has_header=False):
    """Load edges in CSV format as numpy ndarray of strings.

    Args:
        fpath (str): edges file
        delimiter (str): alternative argument name for sep (default=None)
        has_header (bool): True if has header row

    Returns:
        np.ndarray: array of edges
    """
    if PANDAS_INSTALLED:
        header = 'infer' if has_header else None
        df = pd.read_csv(fpath, delimiter=delimiter, header=header)
        edges = df.values
    else:
        logger.warning("Pandas not installed. Using numpy to load csv, which "
                       "is slower.")
        header = 1 if has_header else 0
        edges = np.genfromtxt(fpath, delimiter=delimiter, skip_header=header,
                              dtype=object)
    return edges.astype('str')


def save_graph(filename, csr_matrix, labels=None):
    np.savez(filename,
             data=csr_matrix.data,
             indices=csr_matrix.indices,
             indptr=csr_matrix.indptr,
             shape=csr_matrix.shape,
             labels=labels)
    return filename


def load_graph(filename):
    loader = np.load(filename)
    sp = sps.csr_matrix((loader['data'], loader['indices'], loader['indptr']),
                        shape=loader['shape'])
    return sp, loader['labels']
