#! /usr/bin/env python3

from optparse import OptionParser
from gvassoc.gzindex import GzipFile


def main():
    usage = "Usage: %prog [options] your_table.txt.gz key"
    parser = OptionParser(usage=usage)
    (options, args) = parser.parse_args()
    (fpath, key) = args

    fgzip = GzipFile(fpath)
    print(fgzip.query(key))


if __name__ == "__main__":
    main()