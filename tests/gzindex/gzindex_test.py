from nose.tools import *
from gvassoc.gzindex import GzipIndex
from io import BytesIO

# def setup():
#
# def teardown():
#     print("TEAR DOWN!")

class TestGzIndex:
    def setup(self):
        self.gzindex = GzipIndex()
        self.gzindex.register('x', 1000)
        self.gzindex.register('y', 2000)

    def test_register_and_rescue_index(self):
        assert self.gzindex.index('x') == 1000
        assert self.gzindex.index('y') == 2000

    def test_binary_conversion(self):
        io = BytesIO()
        for entry in self.gzindex.to_binary(): io.write(entry)
        io.seek(0)

        local_gzindex = GzipIndex()
        local_gzindex.from_binary(io)

        assert self.gzindex.index('x') == local_gzindex.index('x')
        assert self.gzindex.index('y') == local_gzindex.index('y')
