from nose.tools import *
from gvassoc.gzindex import GzipIndexer, GzipIndex
from io import StringIO, BytesIO

class TestGzipIndexer:
    def setup(self):
        self.data = StringIO("X\t1000\nY\t2000\nZ\t250\n")
        self.gzindexer = GzipIndexer(self.data)


    def test_building(self):
        gzindex = self.gzindexer.build()

        assert gzindex.has_key("X")
        assert gzindex.has_key("Y")
        assert gzindex.has_key("Z")

    def test_indexing(self):
        gzindex = self.gzindexer.build()

        self.data.seek(gzindex.index("Y"))
        assert self.data.readline() == "Y\t2000\n"
        self.data.seek(gzindex.index("X"))
        assert self.data.readline() == "X\t1000\n"

    def test_saving(self):
        io = BytesIO()
        gzindex = self.gzindexer.build()

        self.gzindexer.save(io)
        io.seek(0)
        local_gzindex = GzipIndex()
        local_gzindex.from_binary(io)

        assert gzindex.index("X") == local_gzindex.index("X")
        assert gzindex.index("Y") == local_gzindex.index("Y")
        assert gzindex.index("Z") == local_gzindex.index("Z")