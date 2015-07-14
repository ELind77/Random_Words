"""
Improves and modifies RandomWords to include constraints for
rhyming and syllable count.

Preserves the essence of the Markov Chain by continuing to use
previous word as current state and choosing the next word based
on observed frequencies following that word, but now also includes
a rhyme goal, and syllable count goal in the current state.  This
could also be interpreted as having a memory and thus violating
the markov property, but I'm not choosing to interpret it that way.

Scheme is of the form \d+[a-z][], e.g. [5a, 7b, 5a] syllable count and
rhyme scheme.
"""

__author__ = 'Eric'


from random_words import RandomWords

import re
import fuzzy
from copy import deepcopy
import random


#
# Globals
#
DMETA = fuzzy.DMetaphone()


#
# Classes
#

class RandomPoem(RandomWords):
    """
    Expects to be instantiated with a model for now.
    """
    def __init__(self, scheme, model=None):
        super(RandomPoem, self).__init__()
        self.scheme = scheme
        if type(model) == str:
            self.load(model)
        # Poem properties
        self.best = None
        self.lines = []
        # Dict matching rhyming letter to words
        self.rhymes = {}

    @staticmethod
    def __get_s_count(line_rep):
        return int(re.match('(\d+)', line_rep).group(0))

    def __get_r_goal(self, line_rep):
        """
        Gets the word to rhyme with
        :param line_rep: scheme representation of line
        :type line_rep: str|None
        :rtype str
        """
        if not line_rep:
            return None
        # Otherwise, get the last line with the matching scheme
        r_letter = re.search('([a-z]+)', line_rep).groups(0)[0]
        if r_letter in self.rhymes:
            return self.rhymes[r_letter][-1]
        else:
            return None

    def __make_init_queue(self):
        t = self._get_itoken(None)
        return [t]

    def __make_queue(self, root_word=None):
        return WordQueue(root_word, self.prob_dict)

    def __add_line(self, new_line, line_rep):
        # Add to array
        if new_line:
            self.lines.append(new_line)
        # If the line is Nil, use best
        elif self.best:
            self.lines.append(self.best)
        else:
            raise Exception("No valid poems!")
        # Add rhymes
        r_letter = re.search('([a-z]+)', line_rep).groups(0)[0]
        if r_letter not in self.rhymes:
            self.rhymes[r_letter] = []
        self.rhymes[r_letter].append(self.lines[-1][-1])

    def __get_line(self, queue, line):
        """
        Returns either None or a valid line
        :param queue:
        :param line:
        :return:
        """
        # Queue lets us iterate through possible word choices for each word.
        # Each level of recursion is a word
        for word in queue:
            # Add new token to the line
            l = line.add(word)
            # Update Best
            if l.better(self.best):
                self.best = l
            # TODO: Could refactor to use ints? 0, -1, 1
            # BC1: We Got it!
            if l.valid():
                return l
            # BC2: Too long, try next word
            if l.over():
                continue
            # Recursive Case: Keep going down the line
            new_l = self.__get_line(self.__make_queue(word), l)
            # If it's a valid line, return it, otherwise got to the next word
            if new_l:
                return new_l
        # BC: 3 Exhausted queue
        return None

    def clear(self):
        self.best = None
        self.lines = []
        self. rhymes = {}

    def run(self):
        self.clear()
        queue = self.__make_init_queue()
        line = Line(self.__get_s_count(self.scheme[0]),
                    self.__get_r_goal(None))
        for i, l in enumerate(self.scheme):
            self.__add_line(self.__get_line(queue, line), l)
            # Break if we're at the end
            if i >= len(self.scheme) - 1:
                break
            # Make the next line
            queue = self.__make_queue(self.lines[-1][-1])
            line = Line(self.__get_s_count(self.scheme[i+1]),
                        self.__get_r_goal(self.scheme[i+1]))
            self.best = None

        return '\n'.join(str(l) for l in self.lines)


class Line(object):
    """Wrapper for a line of text"""
    def __init__(self, s_goal, r_goal, tolerance=2, tokens=None):
        """
        :param s_goal: Syllable count goal for the line
        :param r_goal: Rhyme goal for the line
        :type r_goal: str
        :param tolerance: +- goal for syllable count and rhyme distance
        :param tokens: Used for copying this line
        :return: None
        """
        self.s_goal = s_goal
        self.r_goal = r_goal
        self.i_tolerance = tolerance
        self.r_tolerance = 1
        self.s_tolerance = tolerance
        if tokens:
            self.tokens = tokens
        else:
            self.tokens = []

    def __len__(self):
        return len(self.tokens)

    def __getitem__(self, key):
        return self.tokens[key]

    def __str__(self):
        return ' '.join(t for t in self.tokens)

    def add(self, word):
        """Adds a word to this line and returns a copy of this line"""
        return Line(self.s_goal, self.r_goal,
                    tolerance=self.i_tolerance,
                    tokens=self.tokens + [word])

    #
    # Scoring functions
    #
    def score(self):
        """
        Gets the score of this line based on goals.
        Lower score is better.
        :rtype int
        """
        # Maybe sum the difference between actual and goal for both
        # s_count and rhyme?
        if len(self.tokens) == 0:
            return 0
        return self.__get_s_dist() + self.__rhyme_dist()

    def better(self, l):
        """Returns true if this line has a better score than the given line"""
        if not l:
            return True
        return self.score() < l.score()

    def valid(self):
        """
        Returns True if this line is valid, False otherwise
        :rtype bool
        """
        # TODO: Make this a bit smarter
        # if self.score() <= sum([self.r_tolerance, self.s_tolerance]):
        #     return True
        if self.__get_s_dist() <= self.s_tolerance and self.__rhyme_dist() <= self.r_tolerance:
            return True
        else:
            return False

    def over(self):
        """Returns True if this line is well over the required token/syllable count."""
        # TODO: Maybe have a configurable threshold?
        return (self.__get_s_count() - self.s_goal) > self.s_tolerance

    def __get_s_dist(self):
        return abs(self.s_goal - self.__get_s_count())

    def __get_s_count(self):
        """Returns the current syllable count.
        For now, just returns the number of words"""
        return len(self.tokens)

    def __rhyme_dist(self):
        """Returns the distance of the current word from the rhyme_goal.

        """
        # Could use levenshtien, but just doing basic for now
        # Could also experiment with weighting sounds at the end more highly?

        # No goal
        if not self.r_goal:
            return 0

        # Get the phonetic structure and reverse the strings
        # goal = fuzzy.nysiis(self.r_goal)[::-1]
        # actual = fuzzy.nysiis(self.tokens[-1])[::-1]
        goal = DMETA(self.r_goal)[0][::-1]
        try:
            actual = DMETA(self.tokens[-1])[0][::-1]
        except:
            print self.tokens
            raise
        l = min(2, len(goal), len(actual))
        dist = 0

        for i in range(l):
            if goal[i] != actual[i]:
                dist += 1

        return dist


# WordQueue
class WordQueue(object):
    """Generates queue of words"""
    def __init__(self, root_word, prob_dict):
        # str
        self.root_word = root_word
        # {str: int}
        self.map = deepcopy(prob_dict.map[root_word])

    def __iter__(self):
        while len(self.map) > 0:
            # New random number and sum
            rnd = random.randint(1, sum(self.map.values()))
            summ = 0
            choice = None

            # Select token with probability weighted by
            # observed frequency in model
            for t, f in deepcopy(self.map).iteritems():
                summ += f
                if summ >= rnd:
                    choice = t
                    break

            # Yield the token
            yield choice

            # Pop term from map so that it doesn't get chosen again
            self.map.pop(choice, None)
