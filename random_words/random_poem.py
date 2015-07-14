"""
Improves and modifies RandomWords to include constraints for
rhyming and syllable count.

Presereves the essence of the Markov Chain by continuing to use
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
        return re.match('(\d+)', line_rep).group(0)

    def __get_r_goal(self, line_rep):
        """Gets the word to rhyme with"""
        if not line_rep:
            return None
        # Otherwise, get the last line with the matching scheme
        r_letter = re.search('[a-z]+', line_rep)
        return self.rhymes[r_letter][-1], r_letter

    def __make_init_queue(self):
        t = self.__get_itoken(None)
        return [t]

    def __make_queue(self, root_word=None):
        return WordQueue(root_word)

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
        r_letter = re.search('[a-z]+', line_rep)
        if r_letter not in self.rhymes:
            self.rhymes[r_letter] = []
        self.rhymes[r_letter].append(new_line[-1])

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

    def run(self):
        queue = self.__make_init_queue()
        line = Line(self.__get_s_count(self.scheme[0]),
                    self.__get_r_goal(None))
        for i, l in enumerate(self.scheme):
            self.__add_line(self.__get_line(queue, line), l)
            # Break if we're at the end
            if i >= len(self.scheme):
                break
            queue = self.__make_queue(self.lines[-1][-1])
            line = Line(self.__get_s_count(self.scheme[i+1]),
                        self.__get_r_goal(self.scheme[i+1]))
            self.best = None


class Line(object):
    """Wrapper for a line of text"""
    def __init__(self, s_goal, r_goal, tolerance=2, tokens=None):
        """
        :param s_goal: Syllable count goal for the line
        :param r_goal: Rhyme goal for the line
        :param tolerance: +- goal for syllable count
        :param tokens: Used for copying this line
        :return: None
        """
        self.s_goal = s_goal
        self.r_goal = r_goal
        self.tolerance = tolerance
        if tokens:
            self.tokens = tokens
        else:
            self.tokens = []

    def __len__(self):
        return len(self.tokens)

    def __getitem__(self, key):
        return self.tokens[key]

    def add(self, word):
        """Adds a word to this line and returns a copy of this line"""
        return Line(self.s_goal, self.r_goal,
                    self.tolerance, self.tokens + [word])

    def valid(self):
        """Returns True if this line is valid, False otherwise"""
        pass

    def over(self):
        """Returns True if this line is over the required token/syllable count"""
        pass

    def __get_s_count(self):
        pass

    def __is_rhyme(self):
