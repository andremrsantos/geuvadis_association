#! /usr/bin/env python3
import sys, os

project_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
sys.path.insert(0, project_folder)

from optparse import OptionParser
from lib.gzindex import GzipFile


def main():
    usage = "Usage: %prog [options] your_table.txt.gz key"
    parser = OptionParser(usage=usage)
    (options, args) = parser.parse_args()

    ## Argument checking
    if len(args) < 2:
        exception(parser, "Too few arguments, check our help with `--help`")

    (fpath, key) = args

    fgzip = GzipFile(fpath)
    print(fgzip.query(key))


def exception(parser, msg):
    print("ERROR: %s" % msg)
    parser.print_help()
    exit()

if __name__ == "__main__":
    main()