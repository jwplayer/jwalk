#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""jwalk CLI.

Prompt parameters:
  debug:            drop a debugger if an exception is raised
  delimiter:        delimiter for input file
  embedding-size:   dimension of word2vec embedding (default=200)
  has-header:       boolean if csv has header row
  help (-h):        argparse help
  input (-i):       file input (edgelist of 2/3 cols or adjacency matrix)
  log-level (-l)    logging level (default=INFO)
  model (-m):       use a pre-existing model
  num-walks (-n):   number of of random walks per graph (default=1)
  output (-o):      file output
  stats:            boolean to calculate walk statistics [requires pandas]
  undirected:       make graph undirected
  walk-length:      length of random walks (default=10)
  window-size:      word2vec window size (default=5)
  workers:          number of workers (default=multiprocessing.cpu_count)

Notes:
  To load graph as input, file must be of type npz and with keys:
  'data', 'indices', 'indptr', 'shape', 'labels'
  Labels must be labels of the indices.

Usage:
  jwalk -i tests/data/karate.edgelist -o karate.embeddings --delimiter=' '
"""
import sys
import os.path
import logging
import tempfile
import multiprocessing
from argparse import RawDescriptionHelpFormatter, ArgumentParser

from jwalk import (build_adjacency_matrix, build_corpus, train_model,
                   walk_graph, load_edges, load_graph, save_graph)

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

logger = logging.getLogger(__name__)
LOGFORMAT = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'


def debug_hook(type_, value, tb):
    if hasattr(sys, 'ps1') or not sys.stderr.isatty():
        sys.__excepthook__(type_, value, tb)
    else:
        import traceback
        import pdb
        traceback.print_exception(type_, value, tb)
        print(u"\n")
        pdb.pm()


def create_parser():
    parser = ArgumentParser(description=__doc__,
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--delimiter')
    parser.add_argument('--embedding-size', default=200, type=int)
    parser.add_argument('--graph-path')
    parser.add_argument('--has-header', action='store_true')
    parser.add_argument('--input', '-i', dest='infile', required=True)
    parser.add_argument('--log-level', '-l', type=str.upper, default='INFO')
    parser.add_argument('--num-walks', default=1, type=int)
    parser.add_argument('--model', '-m', dest='model_path')
    parser.add_argument('--output', '-o', dest='outfile', required=True)
    parser.add_argument('--stats', action='store_true')
    parser.add_argument('--undirected', action='store_true')
    parser.add_argument('--walk-length', default=10, type=int)
    parser.add_argument('--window-size', default=5, type=int)
    parser.add_argument('--workers', default=multiprocessing.cpu_count(),
                        type=int)
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    print("Args: ", args)

    if args.debug:
        sys.excepthook = debug_hook

    numeric_level = getattr(logging, args.log_level, None)
    logging.basicConfig(format=LOGFORMAT)
    logger.setLevel(numeric_level)

    return jwalk(**vars(args))


def jwalk(infile, outfile, num_walks=2, embedding_size=100, window_size=5,
          walk_length=10, delimiter=None, model_path=None, stats=False,
          has_header=False, workers=3, undirected=False, **kw):

    outpath = os.path.join(DIR_PATH, '../output')
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    if infile.lower().endswith('.npz'):  # load graph file instead of edges
        logger.debug("Detected npz extension. Assuming input is CSR matrix.")
        logger.info("Loading graph from %s", infile)
        graph, labels = load_graph(infile)
    else:
        logger.info("Loading edges from %s", infile)
        edges = load_edges(infile, delimiter, has_header)
        logger.debug("Loaded edges of shape %s", edges.shape)

        logger.info("Building adjacency matrix")
        graph, labels = build_adjacency_matrix(edges, undirected)
        logger.debug("Number of unique nodes: %d", len(labels))

        graph_path = os.path.join(outpath, 'graph.npz')
        logger.info("Saving graph to %s", graph_path)
        save_graph(graph_path, graph, labels)

    logger.info("Doing %d random walks of length %d", num_walks, walk_length)
    random_walks, word_freq = walk_graph(graph, labels, walk_length, num_walks,
                                         workers)
    logger.debug("Walks shape: %s", random_walks.shape)

    if stats:
        import pandas as pd
        df = pd.DataFrame(random_walks)
        unique_nodes_in_path = df.apply(lambda x: x.nunique(), axis=1)
        logger.info("Unique nodes per walk description: \n" +
                    unique_nodes_in_path.describe().__repr__())

    logger.info("Building corpus from walks")
    with tempfile.NamedTemporaryFile(delete=False) as f_corpus:
        build_corpus(random_walks, outpath=f_corpus.name)

        logger.info("Running Word2Vec on corpus")
        corpus_count = len(labels) * num_walks
        model = train_model(f_corpus.name, embedding_size, window_size,
                            workers=workers, model_path=model_path,
                            word_freq=word_freq, corpus_count=corpus_count)
        model.save(outfile)
        logger.info("Model saved: %s", outfile)

    return outfile
