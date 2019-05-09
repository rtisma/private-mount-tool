# -*- coding: utf-8 -*-

__version__ = "0.1.0"


import sys
import os
import argparse

# if you had a stuff.py in this same directory, you would include the following

def getOptions():
    version_str = '%(prog)s' + " Version %s" % str(__version__)
    parser = argparse.ArgumentParser(description="This is the description")

    parser.add_argument('--version',
            action="version",
            help="Prints program version and exits",
            version=version_str)

    parser.add_argument('-f','--file',
            dest="filename",
            help='input filename',
            nargs='+', #multiple inputs for the -f argument
            metavar='fn')

    parser.add_argument("-q", "--quiet",
            action="store_false", dest="verbose", default=True,
            help="quite mode")


    #A help option is not needed, as it is automatically called when
    # -h or --help is used. The script automatically calls
    # parser.print_help()

    #this creates an option group. Forexample, mandatory and optional arguments
    group = parser.add_argument_group("Mandatory Options",
            "NOTE: These are MANDATORY options. "
            " So do it")
    group.add_argument("-o", dest="output", metavar="<filename>",
            help="This is the group option for output")

    #This actually parses the input arguments and stores them
    # based on the option definitions
    options = parser.parse_args()

    return options


# command line
def main():
    print("Executing %s version %s." % (__name__, __version__))
    if not os.geteuid() == 0:
        sys.exit("\n[ERROR]: Only root can run this script\n")
    options = getOptions()

