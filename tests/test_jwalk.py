# -*- coding: utf-8 -*-
"""py.test unittests"""
import os
import tempfile

try:
    from unittest import mock
except ImportError:
    import mock

import gensim
import numpy as np
import scipy.sparse as sps

from jwalk import corpus
from jwalk import graph
from jwalk import io
from jwalk import skipgram
from jwalk import __main__

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
KARATE_EDGELIST = os.path.join(DIR_PATH, 'data/karate.edgelist')
KARATE_EMBEDDINGS = os.path.join(DIR_PATH, 'data/karate.embeddings')
KARATE_GRAPH = os.path.join(DIR_PATH, 'data/karate.npz')
TEST_CORPUS = os.path.join(DIR_PATH, 'data/corpus.txt.gzip')

TEST_LABELS = np.array(['A', 'B', 'C'])
TEST_CSR = sps.csr_matrix([[0.0, 1.0, 0.0],
                           [0.0, 0.0, 0.0],
                           [1.0, 0.0, 0.0]])


def test_normalize_csr_matrix():
    normalized = corpus.normalize_csr_matrix(TEST_CSR)
    assert np.array_equal(normalized.todense(), TEST_CSR.todense())


def test_make_undirected():
    undirected = graph.make_undirected(TEST_CSR)
    assert np.array_equal(undirected.todense(), [[0.0, 1.0, 1.0],
                                                 [1.0, 0.0, 0.0],
                                                 [1.0, 0.0, 0.0]])


def test_random_walks():
    normalized = corpus.normalize_csr_matrix(TEST_CSR)
    random_walks, vocab_cnt = corpus.walk_random(normalized, TEST_LABELS,
                                                 walk_length=3)
    assert np.array_equal(random_walks, [['A', 'B', ''],
                                         ['B', '', ''],
                                         ['C', 'A', 'B']])
    assert np.array_equal(vocab_cnt, [2, 3, 1])


def test_walk_graph():
    random_walks, word_freq = corpus.walk_graph(TEST_CSR, TEST_LABELS,
                                                walk_length=3, num_walks=2)
    assert np.array_equal(random_walks, [['A', 'B', ''],
                                         ['B', '', ''],
                                         ['C', 'A', 'B'],
                                         ['A', 'B', ''],
                                         ['B', '', ''],
                                         ['C', 'A', 'B']])
    assert word_freq == {'A': 4, 'B': 6, 'C': 2}


def test_encode_edges():
    edges = np.array([['A', 'B'],
                      ['A', 'C'],
                      ['B', 'C'],
                      ['B', 'E']])
    nodes = np.unique(edges)
    encoded = graph.encode_edges(edges, nodes)
    assert np.array_equal(encoded, [[0, 1],
                                    [0, 2],
                                    [1, 2],
                                    [1, 3]])


def test_build_adjacency_matrix():
    edges = np.array([['A', 'B'],
                      ['A', 'C'],
                      ['B', 'C'],
                      ['B', 'E']])
    csr_matrix, id2item = graph.build_adjacency_matrix(edges)
    assert len(id2item) == 4
    assert np.array_equal(csr_matrix.todense(), [[0., 1., 1., 0.],
                                                 [0., 0., 1., 1.],
                                                 [0., 0., 0., 0.],
                                                 [0., 0., 0., 0.]])


def test_load_edges():
    edges = io.load_edges(KARATE_EDGELIST, delimiter=' ', has_header=False)
    assert np.array_equal(edges[0], ['1', '32'])
    assert edges.shape == (78, 2)


@mock.patch('jwalk.io.PANDAS_INSTALLED', False)
def test_load_edges_no_pandas():
    edges = io.load_edges(KARATE_EDGELIST, delimiter=' ')
    assert np.array_equal(edges[0], ['1', '32'])
    assert edges.shape == (78, 2)


def test_build_corpus():
    with tempfile.NamedTemporaryFile() as f:
        random_walks, word_freqs = corpus.walk_graph(TEST_CSR, TEST_LABELS)
        corpus_path = corpus.build_corpus(random_walks, outpath=f.name)
        assert corpus_path == f.name


def test_train_model():
    model = skipgram.train_model(TEST_CORPUS, size=50, window=5)
    assert len(model.wv.vocab) == 31
    assert model.window == 5
    assert model.vector_size == 50
    assert model.sg == 1


def test_train_skipgram():
    walk_length = 4
    num_walks = 2
    corpus_count = num_walks * len(TEST_LABELS)
    random_walks, word_freq = corpus.walk_graph(TEST_CSR, TEST_LABELS,
                                                walk_length, num_walks)
    with tempfile.NamedTemporaryFile() as f:
        corpus.build_corpus(random_walks, outpath=f.name)
        model = (skipgram
                 .train_model(f.name, size=50, window=5, word_freq=word_freq,
                              corpus_count=corpus_count))
        assert len(model.wv.vocab) == 3
        assert model.window == 5
        assert model.vector_size == 50


def test_jwalk():
    with tempfile.NamedTemporaryFile() as f:
        res = __main__.jwalk(KARATE_EDGELIST, outfile=f.name, delimiter=' ')
        assert res == f.name


def test_online():
    with tempfile.NamedTemporaryFile() as f:
        res = __main__.jwalk(KARATE_EDGELIST, outfile=f.name, delimiter=' ',
                             model_path=KARATE_EMBEDDINGS)
        assert res == f.name


def test_gensim_load():
    with tempfile.NamedTemporaryFile() as f:
        __main__.jwalk(KARATE_EDGELIST, outfile=f.name, delimiter=' ')
        model = gensim.models.Word2Vec.load(f.name)
        assert '1' in model.wv.vocab


def test_adjacency():
    with tempfile.NamedTemporaryFile() as f:
        res = __main__.jwalk(KARATE_GRAPH, outfile=f.name, delimiter=' ')
        assert res == f.name


def test_parser():
    parser = __main__.create_parser()
    args = parser.parse_args(['--input', 'infile', '--output', 'outfile'])
    assert args.infile == 'infile'
    assert args.outfile == 'outfile'
