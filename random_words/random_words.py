#!/usr/bin/env python2

"""
A simple random language generator.  When fed a corpus one document at a time,
this program will collect the frequencies with which words follow each other.
Then, given a random word, or a random seed, will generate language in the fashion
of a simple markov chain.
"""

__author__ = 'eric'

import utils

from collections import defaultdict
import random
import cPickle as pickle
import os


# TODO:
#  - Use gensim to translate all input text to lower ASCII
#      - Translate html characters/accents to ASCII


#
# Helpers
#


class FileGen(object):
    """Generator to yield file names from a directory"""
    def __init__(self, dirr):
        if not os.path.exists(dirr):
            raise Exception("Given directory doesn't exist!\n %s" % dirr)
        self.dirr = dirr
        if len([f for f in os.listdir(self.dirr) if os.path.splitext(f)[1] == '.txt']) == 0:
            raise Exception("No text files in given directory!")

    def __iter__(self):
        for f in os.listdir(self.dirr):
            f_path = os.path.join(self.dirr, f)
            if os.path.isfile(f_path) and os.path.splitext(f_path)[1] == '.txt':
                yield f_path


#
# Main functions
#

class RandomWords(object):
    """
    Main class for the project.
    Builds a probability model for words from a corpus and can
    generate new words from that model.
    """
    def __init__(self, corpus_dir=None, newlines=False, uniq_lines=False):
        """
        Expects a string path to a directory containing .txt files to build a model from.
        If no path is given, the model can be added to later wit add_to_model
        :param corpus_dir: Path to get corpus from
        :return: None
        """
        if corpus_dir and not os.path.exists(corpus_dir):
            raise Exception("Given directory doesn't exist!\n %s" % corpus_dir)
        self.newlines = newlines
        self.uniq_lines = uniq_lines
        self.seed = None
        self.init_corpus_dir = corpus_dir

        self.prob_dict = ProbDict()
        if corpus_dir:
            self.add_to_model(corpus_dir)

    def add_to_model(self, corpus_dir):
        """Add all txt files in given dir to the model"""
        for f in FileGen(corpus_dir):
            prev = self.__get_first_token(f)
            seen_lines = set()
            for line in open(f, 'r'):
                # Make sure there's content
                if not line.strip():
                    continue
                # Check uniqe lines
                if self.uniq_lines:
                    if line.strip() in seen_lines:
                        continue
                    else:
                        seen_lines.add(line.strip)
                # Tokenize and add to model
                tokens = self.__tokenize(line)
                for t in tokens[1:]:
                    self.prob_dict.add(prev, t)
                    prev = t

    def __get_first_token(self, path):
        # Iterate so that we don't start with a whitespace token
        for line in open(path, 'r'):
            for t in self.__tokenize(line):
                if t.strip():
                    return t

    def __tokenize(self, string):
        """Just splits on spaces for now."""
        # TODO: normalize case and whitespace?
        if self.newlines:
            return string.split(" ")
        return string.split()

    def save(self, path):
        """Pickle probability model for later"""
        utils.ensure_directories_exist(path)
        pickle.dump(self.prob_dict, open(path, 'wb'))
        print "Saved to: %s" % path

    def load(self, path):
        """Loads pickled probDict to replace self.prob_dict"""
        if not os.path.exists(path) or not os.path.isfile(path):
            raise Exception("Given file doesn't exist!\n %s" % path)
        self.prob_dict = pickle.load(open(path, 'rb'))

    def make_words(self, lenn, init_token=None, seed=123):
        """Returns a string of lenn tokens"""
        # Only set seed once so that the model can be used multiple times in one session
        if not self.seed:
            self.seed = seed
            random.seed(seed)
        # Get an initial token to start with
        if not init_token:
            init_token = self._get_itoken(init_token)
        return ' '.join(w for w in GenWords(init_token, self.prob_dict, lenn))

    def _get_itoken(self, itoken):
        """Chooses a random token from the dictionary with uniform probability"""
        return random.choice(self.prob_dict.keys())


class GenWords(object):
    """Iterator object that can produce a random string from a ProbDict"""
    def __init__(self, init_token, prob_dict, lenn):
        """
        :param init_token: First token in the string
        :type init_token: str
        :param prob_dict: ProbDict to get terms from
        :type prob_dict: ProbDict
        :param lenn: Length of the string to product in tokens
        :type lenn: int
        :return:
        """
        self.prev = init_token
        self.prob_dict = prob_dict
        self.lenn = lenn

    def __len__(self):
        return self.lenn

    def __iter__(self):
        for i in xrange(self.lenn):
            self.prev = self.prob_dict.get(self.prev)
            yield self.prev


# ProbDict
class ProbDict(object):
    """
    A dictionary that maps a token to a hash of tokens and the frequency
    which which they have been observed to occur following the given token.

    Can also be used to retrieve a random word given the preceding token.
    """

    def __init__(self):
        self.map = {}

    def keys(self):
        return self.map.keys()

    def values(self):
        return self.map.values()

    def add(self, curr, nxt):
        """
        Add a token and it's following neighbor to the dictionary
        :param curr: The current token
        :type curr: str
        :param nxt: The next token
        :type nxt: str
        :return: None
        """
        if not curr or not nxt:
            print "Bad token given: %s\t%s" % (curr, nxt)
            return
        if curr not in self.map:
            self.map[curr] = defaultdict(int)
        if nxt not in self.map:
            self.map[nxt] = defaultdict(int)
        # Incf curr.next
        self.map[curr][nxt] += 1

    def get(self, token):
        """
        Retrieve a random word following the given word,
        weighted by the previously observed frequency
        :param token: The current word
        :return: str
        """
        # Check that token is in dictionary
        if token not in self.map or not self.map[token]:
            print "Unknown token:  %s" % token
            return "<UNK>"

        # Choose a token
        freqs = self.map[token]
        rnd = random.randint(1, sum(freqs.values()))
        summ = 0

        # Select a random token with probability weighted by the
        # observed frequency by choosing a random integer between
        # 1 and the sum of all frequencies and then summing the
        # frequencies until the sum is greater or equal to the
        # random number and choosing the word at that point in the
        # iteration.

        for t, f in freqs.iteritems():
            summ += f
            if summ >= rnd:
                return t

        # Error catch
        print "Something wrong here!"
        return "<UNK>"
