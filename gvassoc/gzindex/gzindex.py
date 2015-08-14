import gzip
import struct

from os import path


class GzipFile(object):
    def __init__(self, fpath, index_path=None):
        self.__file_checking(fpath)

        self.__file_path = fpath
        if not index_path:
            self.__index_path = fpath + ".idx"
        self.__file  = gzip.open(self.__file_path, 'rb')
        self.__load_index()

    def query(self, key):
        offset = self.__index.index(key)
        self.__file.seek(offset)
        return self.__file.readline()

    def __file_checking(self, fpath):
        ## Check if file exists
        if not (path.exists(fpath) and path.isfile(fpath)):
            message = "Unable to find the file @ `{}`".format(fpath)
            raise ValueError(message)

        ## Check file format
        if not fpath.endswith('.gz'):
            message = "Unable to find gziped file @ `{}`".format(fpath)
            raise ValueError(message)

    def __load_index(self):
        self.__index = None
        if not path.exists(self.__index_path):
            self.__build_index()
        else:
            self.__read_index()

    def __build_index(self):
        idxer = GzipIndexer(self.__file)
        self.__index = idxer.build()
        self.__save_index()

    def __save_index(self):
        with open(self.__index_path, 'wb') as idxout:
            for entry in self.__index.to_binary():
                idxout.write(entry)

    def __read_index(self):
        with open(self.__index_path, 'wb') as idxin:
            self.__index = GzipIndex()
            self.__index.from_binary(idxin)


class GzipIndex(object):
    def __init__(self):
        self.__key_size = 10
        self.__index_key = dict()
        self.__string_fmt = "{:.>%ds}" % self.__key_size
        self.__binary_fmt = "%dsl" % self.__key_size
        self.__binary_size = struct.calcsize(self.__binary_fmt)

    def index(self, key):
        if not self.has_key(key):
            message = "The key '{:}' was not register".format(key)
            raise ValueError(message)
        return self.__index_key[self.__parse_key(key)]

    def register(self, key, index):
        if self.has_key(key):
            message = "The key '{:}' is already registered".format(key)
            raise ValueError(message)

        self.__index_key[self.__parse_key(key)] = index
        return self

    def has_key(self, key):
        return self.__parse_key(key) in self.__index_key

    def to_binary(self):
        return [
            struct.pack(self.__binary_fmt, bytes(key, 'ascii'), index)
            for key, index in self.__index_key.items()
            ]

    def from_binary(self, binaries):
        while True:
            entry = binaries.read(self.__binary_size)
            if not entry: break

            key, index = struct.unpack(self.__binary_fmt, entry)
            self.register(key.decode('ascii'), index)
        return self

    def __parse_key(self, key):
        return self.__string_fmt.format(str(key))


class GzipIndexer(object):
    def __init__(self, file, key_position=0, separator="\t"):
        self.__file = file
        self.__key_position = key_position
        self.__separator = separator
        self.__index = GzipIndex()

    def index(self):
        return self.__index

    def build(self):
        position = self.__get_position()

        for line in self.__file:
            key = self.__extract_key(line)
            self.index().register(key, position)
            # update position
            position = self.__get_position()

        return self.index()

    def save(self, bin_file):
        for entry in self.index().to_binary():
            bin_file.write(entry)
        return self

    def __get_position(self):
        return self.__file.tell()

    def __extract_key(self, line):
        return line.split(self.__separator)[self.__key_position]