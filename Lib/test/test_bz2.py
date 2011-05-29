#!/usr/bin/env python3
from test import support
from test.support import TESTFN, precisionbigmemtest, _4G

import unittest
from io import BytesIO
import os
import random
import subprocess
import sys

try:
    import threading
except ImportError:
    threading = None

# Skip tests if the bz2 module doesn't exist.
bz2 = support.import_module('bz2')
from bz2 import BZ2File, BZ2Compressor, BZ2Decompressor

has_cmdline_bunzip2 = sys.platform not in ("win32", "os2emx")

class BaseTest(unittest.TestCase):
    "Base for other testcases."
    TEXT_LINES = [
        b'root:x:0:0:root:/root:/bin/bash\n',
        b'bin:x:1:1:bin:/bin:\n',
        b'daemon:x:2:2:daemon:/sbin:\n',
        b'adm:x:3:4:adm:/var/adm:\n',
        b'lp:x:4:7:lp:/var/spool/lpd:\n',
        b'sync:x:5:0:sync:/sbin:/bin/sync\n',
        b'shutdown:x:6:0:shutdown:/sbin:/sbin/shutdown\n',
        b'halt:x:7:0:halt:/sbin:/sbin/halt\n',
        b'mail:x:8:12:mail:/var/spool/mail:\n',
        b'news:x:9:13:news:/var/spool/news:\n',
        b'uucp:x:10:14:uucp:/var/spool/uucp:\n',
        b'operator:x:11:0:operator:/root:\n',
        b'games:x:12:100:games:/usr/games:\n',
        b'gopher:x:13:30:gopher:/usr/lib/gopher-data:\n',
        b'ftp:x:14:50:FTP User:/var/ftp:/bin/bash\n',
        b'nobody:x:65534:65534:Nobody:/home:\n',
        b'postfix:x:100:101:postfix:/var/spool/postfix:\n',
        b'niemeyer:x:500:500::/home/niemeyer:/bin/bash\n',
        b'postgres:x:101:102:PostgreSQL Server:/var/lib/pgsql:/bin/bash\n',
        b'mysql:x:102:103:MySQL server:/var/lib/mysql:/bin/bash\n',
        b'www:x:103:104::/var/www:/bin/false\n',
        ]
    TEXT = b''.join(TEXT_LINES)
    DATA = b'BZh91AY&SY.\xc8N\x18\x00\x01>_\x80\x00\x10@\x02\xff\xf0\x01\x07n\x00?\xe7\xff\xe00\x01\x99\xaa\x00\xc0\x03F\x86\x8c#&\x83F\x9a\x03\x06\xa6\xd0\xa6\x93M\x0fQ\xa7\xa8\x06\x804hh\x12$\x11\xa4i4\xf14S\xd2<Q\xb5\x0fH\xd3\xd4\xdd\xd5\x87\xbb\xf8\x94\r\x8f\xafI\x12\xe1\xc9\xf8/E\x00pu\x89\x12]\xc9\xbbDL\nQ\x0e\t1\x12\xdf\xa0\xc0\x97\xac2O9\x89\x13\x94\x0e\x1c7\x0ed\x95I\x0c\xaaJ\xa4\x18L\x10\x05#\x9c\xaf\xba\xbc/\x97\x8a#C\xc8\xe1\x8cW\xf9\xe2\xd0\xd6M\xa7\x8bXa<e\x84t\xcbL\xb3\xa7\xd9\xcd\xd1\xcb\x84.\xaf\xb3\xab\xab\xad`n}\xa0lh\tE,\x8eZ\x15\x17VH>\x88\xe5\xcd9gd6\x0b\n\xe9\x9b\xd5\x8a\x99\xf7\x08.K\x8ev\xfb\xf7xw\xbb\xdf\xa1\x92\xf1\xdd|/";\xa2\xba\x9f\xd5\xb1#A\xb6\xf6\xb3o\xc9\xc5y\\\xebO\xe7\x85\x9a\xbc\xb6f8\x952\xd5\xd7"%\x89>V,\xf7\xa6z\xe2\x9f\xa3\xdf\x11\x11"\xd6E)I\xa9\x13^\xca\xf3r\xd0\x03U\x922\xf26\xec\xb6\xed\x8b\xc3U\x13\x9d\xc5\x170\xa4\xfa^\x92\xacDF\x8a\x97\xd6\x19\xfe\xdd\xb8\xbd\x1a\x9a\x19\xa3\x80ankR\x8b\xe5\xd83]\xa9\xc6\x08\x82f\xf6\xb9"6l$\xb8j@\xc0\x8a\xb0l1..\xbak\x83ls\x15\xbc\xf4\xc1\x13\xbe\xf8E\xb8\x9d\r\xa8\x9dk\x84\xd3n\xfa\xacQ\x07\xb1%y\xaav\xb4\x08\xe0z\x1b\x16\xf5\x04\xe9\xcc\xb9\x08z\x1en7.G\xfc]\xc9\x14\xe1B@\xbb!8`'

    if has_cmdline_bunzip2:
        def decompress(self, data):
            pop = subprocess.Popen("bunzip2", shell=True,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
            pop.stdin.write(data)
            pop.stdin.close()
            ret = pop.stdout.read()
            pop.stdout.close()
            if pop.wait() != 0:
                ret = bz2.decompress(data)
            return ret

    else:
        # bunzip2 isn't available to run on Windows.
        def decompress(self, data):
            return bz2.decompress(data)

class BZ2FileTest(BaseTest):
    "Test BZ2File type miscellaneous methods."

    def setUp(self):
        self.filename = TESTFN

    def tearDown(self):
        if os.path.isfile(self.filename):
            os.unlink(self.filename)

    def createTempFile(self, streams=1):
        with open(self.filename, "wb") as f:
            f.write(self.DATA * streams)

    def testRead(self):
        self.createTempFile()
        with BZ2File(self.filename) as bz2f:
            self.assertRaises(TypeError, bz2f.read, None)
            self.assertEqual(bz2f.read(), self.TEXT)

    def testReadMultiStream(self):
        self.createTempFile(streams=5)
        with BZ2File(self.filename) as bz2f:
            self.assertRaises(TypeError, bz2f.read, None)
            self.assertEqual(bz2f.read(), self.TEXT * 5)

    def testReadMonkeyMultiStream(self):
        # Test BZ2File.read() on a multi-stream archive where a stream
        # boundary coincides with the end of the raw read buffer.
        buffer_size = bz2._BUFFER_SIZE
        bz2._BUFFER_SIZE = len(self.DATA)
        try:
            self.createTempFile(streams=5)
            with BZ2File(self.filename) as bz2f:
                self.assertRaises(TypeError, bz2f.read, None)
                self.assertEqual(bz2f.read(), self.TEXT * 5)
        finally:
            bz2._BUFFER_SIZE = buffer_size

    def testRead0(self):
        self.createTempFile()
        with BZ2File(self.filename) as bz2f:
            self.assertRaises(TypeError, bz2f.read, None)
            self.assertEqual(bz2f.read(0), b"")

    def testReadChunk10(self):
        self.createTempFile()
        with BZ2File(self.filename) as bz2f:
            text = b''
            while True:
                str = bz2f.read(10)
                if not str:
                    break
                text += str
            self.assertEqual(text, self.TEXT)

    def testReadChunk10MultiStream(self):
        self.createTempFile(streams=5)
        with BZ2File(self.filename) as bz2f:
            text = b''
            while True:
                str = bz2f.read(10)
                if not str:
                    break
                text += str
            self.assertEqual(text, self.TEXT * 5)

    def testRead100(self):
        self.createTempFile()
        with BZ2File(self.filename) as bz2f:
            self.assertEqual(bz2f.read(100), self.TEXT[:100])

    def testPeek(self):
        self.createTempFile()
        with BZ2File(self.filename) as bz2f:
            pdata = bz2f.peek()
            self.assertNotEqual(len(pdata), 0)
            self.assertTrue(self.TEXT.startswith(pdata))
            self.assertEqual(bz2f.read(), self.TEXT)

    def testReadInto(self):
        self.createTempFile()
        with BZ2File(self.filename) as bz2f:
            n = 128
            b = bytearray(n)
            self.assertEqual(bz2f.readinto(b), n)
            self.assertEqual(b, self.TEXT[:n])
            n = len(self.TEXT) - n
            b = bytearray(len(self.TEXT))
            self.assertEqual(bz2f.readinto(b), n)
            self.assertEqual(b[:n], self.TEXT[-n:])

    def testReadLine(self):
        self.createTempFile()
        with BZ2File(self.filename) as bz2f:
            self.assertRaises(TypeError, bz2f.readline, None)
            sio = BytesIO(self.TEXT)
            for line in sio.readlines():
                self.assertEqual(bz2f.readline(), line)

    def testReadLineMultiStream(self):
        self.createTempFile(streams=5)
        with BZ2File(self.filename) as bz2f:
            self.assertRaises(TypeError, bz2f.readline, None)
            sio = BytesIO(self.TEXT * 5)
            for line in sio.readlines():
                self.assertEqual(bz2f.readline(), line)

    def testReadLines(self):
        self.createTempFile()
        with BZ2File(self.filename) as bz2f:
            self.assertRaises(TypeError, bz2f.readlines, None)
            sio = BytesIO(self.TEXT)
            self.assertEqual(bz2f.readlines(), sio.readlines())

    def testReadLinesMultiStream(self):
        self.createTempFile(streams=5)
        with BZ2File(self.filename) as bz2f:
            self.assertRaises(TypeError, bz2f.readlines, None)
            sio = BytesIO(self.TEXT * 5)
            self.assertEqual(bz2f.readlines(), sio.readlines())

    def testIterator(self):
        self.createTempFile()
        with BZ2File(self.filename) as bz2f:
            sio = BytesIO(self.TEXT)
            self.assertEqual(list(iter(bz2f)), sio.readlines())

    def testIteratorMultiStream(self):
        self.createTempFile(streams=5)
        with BZ2File(self.filename) as bz2f:
            sio = BytesIO(self.TEXT * 5)
            self.assertEqual(list(iter(bz2f)), sio.readlines())

    def testClosedIteratorDeadlock(self):
        # Issue #3309: Iteration on a closed BZ2File should release the lock.
        self.createTempFile()
        bz2f = BZ2File(self.filename)
        bz2f.close()
        self.assertRaises(ValueError, bz2f.__next__)
        # This call will deadlock if the above .__next__ call failed to
        # release the lock.
        self.assertRaises(ValueError, bz2f.readlines)

    def testWrite(self):
        with BZ2File(self.filename, "w") as bz2f:
            self.assertRaises(TypeError, bz2f.write)
            bz2f.write(self.TEXT)
        with open(self.filename, 'rb') as f:
            self.assertEqual(self.decompress(f.read()), self.TEXT)

    def testWriteChunks10(self):
        with BZ2File(self.filename, "w") as bz2f:
            n = 0
            while True:
                str = self.TEXT[n*10:(n+1)*10]
                if not str:
                    break
                bz2f.write(str)
                n += 1
        with open(self.filename, 'rb') as f:
            self.assertEqual(self.decompress(f.read()), self.TEXT)

    def testWriteLines(self):
        with BZ2File(self.filename, "w") as bz2f:
            self.assertRaises(TypeError, bz2f.writelines)
            sio = BytesIO(self.TEXT)
            bz2f.writelines(sio.readlines())
        # Issue #1535500: Calling writelines() on a closed BZ2File
        # should raise an exception.
        self.assertRaises(ValueError, bz2f.writelines, ["a"])
        with open(self.filename, 'rb') as f:
            self.assertEqual(self.decompress(f.read()), self.TEXT)

    def testWriteMethodsOnReadOnlyFile(self):
        with BZ2File(self.filename, "w") as bz2f:
            bz2f.write(b"abc")

        with BZ2File(self.filename, "r") as bz2f:
            self.assertRaises(IOError, bz2f.write, b"a")
            self.assertRaises(IOError, bz2f.writelines, [b"a"])

    def testAppend(self):
        with BZ2File(self.filename, "w") as bz2f:
            self.assertRaises(TypeError, bz2f.write)
            bz2f.write(self.TEXT)
        with BZ2File(self.filename, "a") as bz2f:
            self.assertRaises(TypeError, bz2f.write)
            bz2f.write(self.TEXT)
        with open(self.filename, 'rb') as f:
            self.assertEqual(self.decompress(f.read()), self.TEXT * 2)

    def testSeekForward(self):
        self.createTempFile()
        with BZ2File(self.filename) as bz2f:
            self.assertRaises(TypeError, bz2f.seek)
            bz2f.seek(150)
            self.assertEqual(bz2f.read(), self.TEXT[150:])

    def testSeekForwardAcrossStreams(self):
        self.createTempFile(streams=2)
        with BZ2File(self.filename) as bz2f:
            self.assertRaises(TypeError, bz2f.seek)
            bz2f.seek(len(self.TEXT) + 150)
            self.assertEqual(bz2f.read(), self.TEXT[150:])

    def testSeekBackwards(self):
        self.createTempFile()
        with BZ2File(self.filename) as bz2f:
            bz2f.read(500)
            bz2f.seek(-150, 1)
            self.assertEqual(bz2f.read(), self.TEXT[500-150:])

    def testSeekBackwardsAcrossStreams(self):
        self.createTempFile(streams=2)
        with BZ2File(self.filename) as bz2f:
            readto = len(self.TEXT) + 100
            while readto > 0:
                readto -= len(bz2f.read(readto))
            bz2f.seek(-150, 1)
            self.assertEqual(bz2f.read(), self.TEXT[100-150:] + self.TEXT)

    def testSeekBackwardsFromEnd(self):
        self.createTempFile()
        with BZ2File(self.filename) as bz2f:
            bz2f.seek(-150, 2)
            self.assertEqual(bz2f.read(), self.TEXT[len(self.TEXT)-150:])

    def testSeekBackwardsFromEndAcrossStreams(self):
        self.createTempFile(streams=2)
        with BZ2File(self.filename) as bz2f:
            bz2f.seek(-1000, 2)
            self.assertEqual(bz2f.read(), (self.TEXT * 2)[-1000:])

    def testSeekPostEnd(self):
        self.createTempFile()
        with BZ2File(self.filename) as bz2f:
            bz2f.seek(150000)
            self.assertEqual(bz2f.tell(), len(self.TEXT))
            self.assertEqual(bz2f.read(), b"")

    def testSeekPostEndMultiStream(self):
        self.createTempFile(streams=5)
        with BZ2File(self.filename) as bz2f:
            bz2f.seek(150000)
            self.assertEqual(bz2f.tell(), len(self.TEXT) * 5)
            self.assertEqual(bz2f.read(), b"")

    def testSeekPostEndTwice(self):
        self.createTempFile()
        with BZ2File(self.filename) as bz2f:
            bz2f.seek(150000)
            bz2f.seek(150000)
            self.assertEqual(bz2f.tell(), len(self.TEXT))
            self.assertEqual(bz2f.read(), b"")

    def testSeekPostEndTwiceMultiStream(self):
        self.createTempFile(streams=5)
        with BZ2File(self.filename) as bz2f:
            bz2f.seek(150000)
            bz2f.seek(150000)
            self.assertEqual(bz2f.tell(), len(self.TEXT) * 5)
            self.assertEqual(bz2f.read(), b"")

    def testSeekPreStart(self):
        self.createTempFile()
        with BZ2File(self.filename) as bz2f:
            bz2f.seek(-150)
            self.assertEqual(bz2f.tell(), 0)
            self.assertEqual(bz2f.read(), self.TEXT)

    def testSeekPreStartMultiStream(self):
        self.createTempFile(streams=2)
        with BZ2File(self.filename) as bz2f:
            bz2f.seek(-150)
            self.assertEqual(bz2f.tell(), 0)
            self.assertEqual(bz2f.read(), self.TEXT * 2)

    def testFileno(self):
        self.createTempFile()
        with open(self.filename) as rawf:
            with BZ2File(fileobj=rawf) as bz2f:
                self.assertEqual(bz2f.fileno(), rawf.fileno())

    def testOpenDel(self):
        self.createTempFile()
        for i in range(10000):
            o = BZ2File(self.filename)
            del o

    def testOpenNonexistent(self):
        self.assertRaises(IOError, BZ2File, "/non/existent")

    def testReadlinesNoNewline(self):
        # Issue #1191043: readlines() fails on a file containing no newline.
        data = b'BZh91AY&SY\xd9b\x89]\x00\x00\x00\x03\x80\x04\x00\x02\x00\x0c\x00 \x00!\x9ah3M\x13<]\xc9\x14\xe1BCe\x8a%t'
        with open(self.filename, "wb") as f:
            f.write(data)
        with BZ2File(self.filename) as bz2f:
            lines = bz2f.readlines()
        self.assertEqual(lines, [b'Test'])
        with BZ2File(self.filename) as bz2f:
            xlines = list(bz2f.readlines())
        self.assertEqual(xlines, [b'Test'])

    def testContextProtocol(self):
        f = None
        with BZ2File(self.filename, "wb") as f:
            f.write(b"xxx")
        f = BZ2File(self.filename, "rb")
        f.close()
        try:
            with f:
                pass
        except ValueError:
            pass
        else:
            self.fail("__enter__ on a closed file didn't raise an exception")
        try:
            with BZ2File(self.filename, "wb") as f:
                1/0
        except ZeroDivisionError:
            pass
        else:
            self.fail("1/0 didn't raise an exception")

    @unittest.skipUnless(threading, 'Threading required for this test.')
    def testThreading(self):
        # Issue #7205: Using a BZ2File from several threads shouldn't deadlock.
        data = b"1" * 2**20
        nthreads = 10
        with bz2.BZ2File(self.filename, 'wb') as f:
            def comp():
                for i in range(5):
                    f.write(data)
            threads = [threading.Thread(target=comp) for i in range(nthreads)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

    def testMixedIterationAndReads(self):
        self.createTempFile()
        linelen = len(self.TEXT_LINES[0])
        halflen = linelen // 2
        with bz2.BZ2File(self.filename) as bz2f:
            bz2f.read(halflen)
            self.assertEqual(next(bz2f), self.TEXT_LINES[0][halflen:])
            self.assertEqual(bz2f.read(), self.TEXT[linelen:])
        with bz2.BZ2File(self.filename) as bz2f:
            bz2f.readline()
            self.assertEqual(next(bz2f), self.TEXT_LINES[1])
            self.assertEqual(bz2f.readline(), self.TEXT_LINES[2])
        with bz2.BZ2File(self.filename) as bz2f:
            bz2f.readlines()
            with self.assertRaises(StopIteration):
                next(bz2f)
            self.assertEqual(bz2f.readlines(), [])

    def testMultiStreamOrdering(self):
        # Test the ordering of streams when reading a multi-stream archive.
        data1 = b"foo" * 1000
        data2 = b"bar" * 1000
        with BZ2File(self.filename, "w") as bz2f:
            bz2f.write(data1)
        with BZ2File(self.filename, "a") as bz2f:
            bz2f.write(data2)
        with BZ2File(self.filename) as bz2f:
            self.assertEqual(bz2f.read(), data1 + data2)

    # Tests for a BZ2File wrapping another file object:

    def testReadBytesIO(self):
        with BytesIO(self.DATA) as bio:
            with BZ2File(fileobj=bio) as bz2f:
                self.assertRaises(TypeError, bz2f.read, None)
                self.assertEqual(bz2f.read(), self.TEXT)
            self.assertFalse(bio.closed)

    def testPeekBytesIO(self):
        with BytesIO(self.DATA) as bio:
            with BZ2File(fileobj=bio) as bz2f:
                pdata = bz2f.peek()
                self.assertNotEqual(len(pdata), 0)
                self.assertTrue(self.TEXT.startswith(pdata))
                self.assertEqual(bz2f.read(), self.TEXT)

    def testWriteBytesIO(self):
        with BytesIO() as bio:
            with BZ2File(fileobj=bio, mode="w") as bz2f:
                self.assertRaises(TypeError, bz2f.write)
                bz2f.write(self.TEXT)
            self.assertEqual(self.decompress(bio.getvalue()), self.TEXT)
            self.assertFalse(bio.closed)

    def testSeekForwardBytesIO(self):
        with BytesIO(self.DATA) as bio:
            with BZ2File(fileobj=bio) as bz2f:
                self.assertRaises(TypeError, bz2f.seek)
                bz2f.seek(150)
                self.assertEqual(bz2f.read(), self.TEXT[150:])

    def testSeekBackwardsBytesIO(self):
        with BytesIO(self.DATA) as bio:
            with BZ2File(fileobj=bio) as bz2f:
                bz2f.read(500)
                bz2f.seek(-150, 1)
                self.assertEqual(bz2f.read(), self.TEXT[500-150:])

class BZ2CompressorTest(BaseTest):
    def testCompress(self):
        bz2c = BZ2Compressor()
        self.assertRaises(TypeError, bz2c.compress)
        data = bz2c.compress(self.TEXT)
        data += bz2c.flush()
        self.assertEqual(self.decompress(data), self.TEXT)

    def testCompressChunks10(self):
        bz2c = BZ2Compressor()
        n = 0
        data = b''
        while True:
            str = self.TEXT[n*10:(n+1)*10]
            if not str:
                break
            data += bz2c.compress(str)
            n += 1
        data += bz2c.flush()
        self.assertEqual(self.decompress(data), self.TEXT)

    @precisionbigmemtest(size=_4G + 100, memuse=2)
    def testCompress4G(self, size):
        # "Test BZ2Compressor.compress()/flush() with >4GiB input"
        bz2c = BZ2Compressor()
        data = b"x" * size
        try:
            compressed = bz2c.compress(data)
            compressed += bz2c.flush()
        finally:
            data = None  # Release memory
        data = bz2.decompress(compressed)
        try:
            self.assertEqual(len(data), size)
            self.assertEqual(len(data.strip(b"x")), 0)
        finally:
            data = None

class BZ2DecompressorTest(BaseTest):
    def test_Constructor(self):
        self.assertRaises(TypeError, BZ2Decompressor, 42)

    def testDecompress(self):
        bz2d = BZ2Decompressor()
        self.assertRaises(TypeError, bz2d.decompress)
        text = bz2d.decompress(self.DATA)
        self.assertEqual(text, self.TEXT)

    def testDecompressChunks10(self):
        bz2d = BZ2Decompressor()
        text = b''
        n = 0
        while True:
            str = self.DATA[n*10:(n+1)*10]
            if not str:
                break
            text += bz2d.decompress(str)
            n += 1
        self.assertEqual(text, self.TEXT)

    def testDecompressUnusedData(self):
        bz2d = BZ2Decompressor()
        unused_data = b"this is unused data"
        text = bz2d.decompress(self.DATA+unused_data)
        self.assertEqual(text, self.TEXT)
        self.assertEqual(bz2d.unused_data, unused_data)

    def testEOFError(self):
        bz2d = BZ2Decompressor()
        text = bz2d.decompress(self.DATA)
        self.assertRaises(EOFError, bz2d.decompress, b"anything")

    @precisionbigmemtest(size=_4G + 100, memuse=3)
    def testDecompress4G(self, size):
        # "Test BZ2Decompressor.decompress() with >4GiB input"
        blocksize = 10 * 1024 * 1024
        block = random.getrandbits(blocksize * 8).to_bytes(blocksize, 'little')
        try:
            data = block * (size // blocksize + 1)
            compressed = bz2.compress(data)
            bz2d = BZ2Decompressor()
            decompressed = bz2d.decompress(compressed)
            self.assertTrue(decompressed == data)
        finally:
            data = None
            compressed = None
            decompressed = None


class FuncTest(BaseTest):
    "Test module functions"

    def testCompress(self):
        data = bz2.compress(self.TEXT)
        self.assertEqual(self.decompress(data), self.TEXT)

    def testDecompress(self):
        text = bz2.decompress(self.DATA)
        self.assertEqual(text, self.TEXT)

    def testDecompressEmpty(self):
        text = bz2.decompress(b"")
        self.assertEqual(text, b"")

    def testDecompressIncomplete(self):
        self.assertRaises(ValueError, bz2.decompress, self.DATA[:-10])

    def testDecompressMultiStream(self):
        text = bz2.decompress(self.DATA * 5)
        self.assertEqual(text, self.TEXT * 5)

def test_main():
    support.run_unittest(
        BZ2FileTest,
        BZ2CompressorTest,
        BZ2DecompressorTest,
        FuncTest
    )
    support.reap_children()

if __name__ == '__main__':
    test_main()
