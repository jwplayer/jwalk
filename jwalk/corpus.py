# -*- coding: utf-8 -*-
"""Generate text corpus from random walks on graph."""
import numpy as np
from joblib import Parallel, delayed
from joblib.pool import has_shareable_memory

from jwalk import walks

__all__ = ['walk_graph', 'build_corpus']


def walk_random(normalized_csr, labels, walk_length):
    """Generate random walks for each node in a normalized sparse csr matrix.

    Args:
        normalized_csr (scipy.sparse.csr_matrix): normalized adjacency matrix
        labels (np.ndarray): array of node labels
        walk_length (int): length of walk

    Returns:
        np.array walks, np.array word frequencies
    """
    # need to wrap walks.walk_random otherwise joblib complains in Py2
    return walks.walk_random(normalized_csr, labels, walk_length)


def normalize_csr_matrix(csr_matrix):
    """Normalize adjacency matrix weights.

    Args:
        scipy.sparse.csr_matrix: adjacency matrix

    Returns:
        scipy.sparse.csr_matrix
    """
    row_sums = np.array(csr_matrix.sum(axis=1))[:, 0]
    row_indices, col_indices = csr_matrix.nonzero()

    normalized = csr_matrix.copy()
    normalized.data /= row_sums[row_indices]
    return normalized


def walk_graph(csr_matrix, labels, walk_length=40, num_walks=1, n_jobs=1):
    """Perform random walks on adjacency matrix.

    Args:
        csr_matrix: adjacency matrix.
        labels: list of node labels where index align with CSR matrix
        walk_length: maximum length of random walk (default=40)
        num_walks: number of walks to do for each node
        n_jobs: number of cores to use (default=1)

    Returns:
        np.ndarray: list of random walks
    """
    normalized = normalize_csr_matrix(csr_matrix)

    results = (Parallel(n_jobs=n_jobs)
               (delayed(walk_random, has_shareable_memory)
                (normalized, labels, walk_length)
                for _ in range(num_walks)))

    walks, freqs = zip(*results)

    random_walks = np.concatenate(walks)
    word_freqs = np.sum(freqs, axis=0)

    return random_walks, dict(zip(labels, word_freqs))


def build_corpus(walks, outpath):
    """Build corpus by shuffling and then saving as text file.

    Args:
        walks: random walks
        outpath: file to write to

    Returns:
        str: file path of corpus
    """
    np.random.shuffle(walks)
    np.savetxt(outpath, walks, delimiter=' ', fmt='%s')
    return outpath
