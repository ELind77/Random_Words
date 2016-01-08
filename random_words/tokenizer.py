"""
Tokenizer class for project.  Generator class instantiated with a string
that will then yield tokens one at a time.
"""

from __future__ import unicode_literals
import string
import re
import itertools
from spacy.en import English


__author__ = 'eric'

#
# Globals
#

# Whitespace patterns
RE_WHITESPACE = re.compile(r"(\s)+", re.UNICODE)
RE_MULTINEWLINE = re.compile(r"([\n]+)", re.UNICODE)
RE_MULTISPACE = re.compile(r"( )+", re.UNICODE)
RE_NEWLINE = re.compile(r"(\n)", re.UNICODE)
# Parser
NLP = English()


# Tokenizer
class Tokenizer(object):
    """
    - Starts with standard model (spacy)
    - Merges hyphenated words
    - Merges multiple newlines to single newline
    - Treats newlines as tokens
    - Option to replace all whitespace with spaces
    - Switch to merge tokens beginning with apostrophes with preceding token
    - Yields non-printing tokens for start_sentence and end_sentence
    - Yields tokens with no whitespace attached (unless the token is a whitespace token)

    """

    def __init__(self, doc, replace_whitespace=True, merge_apostrophes=False):
        """
        :param doc: A string to be tokenized
        :param replace_whitespace: Boolean, if true, replaces all whitespace with strings
        :param merge_apostrophes: Boolean, if true, merges tokens beginning with an apostrophe with the previous token
        :return: None
        """
        self.doc = doc
        self.replace_whitespace = replace_whitespace
        self.merge_apostrophes = merge_apostrophes

    def _preprocess(self, doc):
        # All whitespace => ' '
        if self.replace_whitespace:
            doc = RE_WHITESPACE.sub(" ", doc)
        # Multiple newlines => single newline
        else:
            doc = RE_MULTINEWLINE.sub("\n", doc)

        # Newlines to tokens
        # Spacy does this for me!!!!

        # Replace multiple spaces
        doc = RE_MULTISPACE.sub(" ", doc)

        # Give back the doc
        return doc

    @staticmethod
    def _tokenize(doc):
        return NLP(doc)

    @staticmethod
    def _get_token_string(t):
        if isinstance(t, unicode):
            return t
        else:
            return t.orth_

    def __iter__(self):
        sentences = self._tokenize(self.doc).sents
        prev_token = None

        for sentence in sentences:
            prev_token = '<s>'

            for token in itertools.chain(sentence, ['</s>']):
                curr_token = self._get_token_string(token)

                if prev_token is not None:
                    # Merge hyphens
                    if curr_token[0] == '-':
                        # Could be multiple hyphens so keep going till done
                        prev_token += curr_token
                        continue
                    # Merge apostrophes
                    if self.merge_apostrophes:
                        if curr_token[0] == "'":
                            prev_token += curr_token
                            continue
                            # Multiple apostrophes would be very odd but continue anyways...
                if prev_token:
                    yield prev_token
                prev_token = curr_token

            # Yield the last token
            if prev_token:
                yield prev_token
