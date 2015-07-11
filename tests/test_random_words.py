#!/usr/bin/env python2

"""
Small test suite for Random_Words project.
Meant to be run with nosetests
"""

__author__ = 'eric'

import nose.tools as nosey
import os
import re
from collections import defaultdict

import random_words.random_words as rw


#
# Globals
#

DATA_DIR = os.path.join('tests', 'data', 'kanye')
WS_PATTERN = re.compile(r"(\s)")


#
# Helpers
#

def tokenize(s):
    return WS_PATTERN.sub(" ", s).split()


#
# Tests
#

class TestProbDict(object):
    def __init__(self):
        """This is really here to avoid making my linter angry"""
        self.prob_dict = None
        self.test_tokens = []

    @classmethod
    def setUpClass(cls):
        # cls.kanye_file = os.path.join(DATA_DIR, 'good_morning.txt')
        cls.test_string = (
            "I am the very model of a modern Major-General, "
            "I've information vegetable, animal, and mineral, "
            "I know the kings of England, and I quote the fights historical "
            "From Marathon to Waterloo, in order categorical; "
            "I'm very well acquainted, too, with matters mathematical, "
            "I understand equations, both the simple and quadratical, "
            "About binomial theorem I'm teeming with a lot o' news, "
            "With many cheerful facts about the square of the hypotenuse."
        )
        cls.ws_pattern = re.compile(r"(\s)")

    def setUp(self):
        self.prob_dict = rw.ProbDict()
        self.test_tokens = tokenize(self.test_string)

    def add_tokens(self, tokens):
        prev = tokens[0]
        for t in tokens[1:]:
            self.prob_dict.add(prev, t)
            prev = t

    def test_prob_dict_init(self):
        nosey.assert_is_instance(self.prob_dict, rw.ProbDict)
        nosey.assert_is_instance(self.prob_dict.map, dict)

    def test_prob_dict_add_one(self):
        self.prob_dict.add('I', 'am')
        nosey.assert_items_equal(['I', 'am'], self.prob_dict.keys())
        # Check value types
        for v in self.prob_dict.values():
            nosey.assert_is_instance(v, defaultdict)
        # Check freqs
        nosey.assert_dict_equal({'am': 1}, self.prob_dict.map['I'])

    def test_prob_dict_add_few(self):
        s = "I am the very model of a modern Major-General and I am getting tired of this song."
        toks = tokenize(s)
        self.add_tokens(toks)
        nosey.assert_items_equal(list(set(toks)), self.prob_dict.keys())
        # Check value types
        for v in self.prob_dict.values():
            nosey.assert_is_instance(v, defaultdict)
        # Check freqs (spot check)
        nosey.assert_dict_equal({'am': 2}, self.prob_dict.map['I'])
        nosey.assert_equal(1, self.prob_dict.map['am']['the'])
        nosey.assert_equal(1, self.prob_dict.map['and']['I'])

    def test_prob_dict_add_many(self):
        self.add_tokens(self.test_tokens)
        # Check keys
        nosey.assert_items_equal(list(set(self.test_tokens)), self.prob_dict.keys())
        # Check values
        for v in self.prob_dict.values():
            nosey.assert_is_instance(v, defaultdict)
        # Spot Check
        nosey.assert_dict_equal({'am': 1, 'quote': 1, 'understand': 1, 'know': 1}, self.prob_dict.map['I'])

    def test_prob_dict_get_one(self):
        self.prob_dict.add("I", "am")
        # Test type
        nosey.assert_is_instance(self.prob_dict.get('I'), str)
        # Test value
        nosey.assert_equal("am", self.prob_dict.get('I'))

    def test_prob_dict_get(self):
        self.add_tokens(self.test_tokens)
        # Test type
        nosey.assert_is_instance(self.prob_dict.get('I'), str)
        # Test value
        nosey.assert_in(self.prob_dict.get('I'), ['am', 'quote', 'understand', 'know'])


class TestRandomWords(object):
    def __init__(self):
        self.tokens = []
        self.rw = None

    @classmethod
    def setUpClass(cls):
        cls.kanye_file = os.path.join(DATA_DIR, 'good_morning')

    def setUp(self):
        # with open(self.kanye_file, 'r') as f:
        #     self.tokens = tokenize(f.readlines())
        self.rw = rw.RandomWords()

    def test_init_empty_random_words(self):
        nosey.assert_is_instance(self.rw, rw.RandomWords)
        nosey.assert_is_instance(self.rw.prob_dict, rw.ProbDict)

    def test_init_rw_with_dir(self):
        rw2 = rw.RandomWords(corpus_dir=DATA_DIR)
        nosey.assert_is_instance(rw2, rw.RandomWords)

    def test_rw_rasies_error_for_bad_dir(self):
        nosey.assert_raises(Exception, rw.RandomWords, corpus_dir="/foo")

    def test_rw_kanye(self):
        rw2 = rw.RandomWords(corpus_dir=DATA_DIR)
        words = rw2.make_words(25)
        print words
        nosey.assert_is_instance(words, str)
        nosey.assert_equal(25, len(words.split()))
