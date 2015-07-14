"""
Uitilities file for Random_Words  project
"""


__author__ = 'Eric'


import os


def ensure_directories_exist(path):
    """
    Checks whether directories containing the specified file exist
    and attempts to create them is they don't.
    :param path: str - A path, can optionally end in a file
    :returns str - The path that was created
    """
    # http://stackoverflow.com/questions/273192/in-python-check-if-a-directory-exists-and-create-it-if-necessary
    directory = os.path.dirname(path)
    if directory:
        if not os.path.exists(directory):
            os.makedirs(directory)
