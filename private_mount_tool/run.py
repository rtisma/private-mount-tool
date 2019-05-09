# -*- coding: utf-8 -*-

__version__ = "0.2.0"


import sys

# if you had a stuff.py in this same directory, you would include the following
# from .stuff import Stuff


# command line
def main():
    print("Executing bootstrap version %s." % __version__)
    print("List of argument strings: %s" % sys.argv[1:])


# class Boo(Stuff):
    # pass
