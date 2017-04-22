# -*- coding: utf-8 -*-
"""Build word2vec model."""
import os
import logging

from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence

__all__ = ['train_model']

logger = logging.getLogger(__name__)


def train_model(corpus, size=200, window=5, workers=3, model_path=None,
                word_freq=None, corpus_count=None):
    """Train using Skipgram model.

    Args:
        corpus (str):       file path of corpus
        size (int):         embedding size (default=200)
        window (int):       window size (default=5)
        workers (int):      number of workers (default=3)
        model_path (str):   file path of model we want to update
        word_freq (dict):   dictionary of word frequencies
        corpus_count (int): corpus size

    Returns:
        Word2Vec: word2vec model
    """
    sentences = LineSentence(corpus)
    if model_path is not None:
        logger.info("Updating pre-existing model: %s", model_path)
        assert os.path.isfile(model_path), "File does not exist"
        model = Word2Vec.load(model_path)
        model.build_vocab(sentences, update=True)
        model.train(sentences, total_examples=model.corpus_count,
                    epochs=model.iter)
    else:
        model = Skipgram(sentences=sentences, size=size, window=window,
                         min_count=1, workers=workers, raw_vocab=word_freq,
                         corpus_count=corpus_count)
    return model


class Skipgram(Word2Vec):
    """A subclass to allow more customization of the Word2Vec internals."""

    def __init__(self, raw_vocab=None, corpus_count=None, **kwargs):
        self.raw_vocab = raw_vocab
        self.corpus_count = corpus_count
        super(Skipgram, self).__init__(sg=1, **kwargs)

    def scan_vocab(self, sentences, progress_per=10000, trim_rule=None):
        """Override to supply own word frequencies."""
        if self.corpus_count is None or self.raw_vocab is None:
            super(Skipgram, self).scan_vocab(sentences, progress_per, trim_rule)  # NOQA: E501
