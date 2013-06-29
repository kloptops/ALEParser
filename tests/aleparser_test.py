# This is free and unencumbered software released into the public domain.
# 
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
# 
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
# 
# For more information, please refer to <http://unlicense.org/>

import unittest
import hashlib
import json
from aleparser import ALEParser, ALEError, ALESyntaxError

def digest_data(data):
    return hashlib.md5(json.dumps(data, sort_keys=True)).hexdigest()

class CheckSimpleALE(unittest.TestCase):
    def setUp(self):
        self.file_name = 'tests/simple.ALE'
        self.file_handle = open(self.file_name, 'rU')
        self.file_text = self.file_handle.read()
        self.file_handle.seek(0)

    def test_filename(self):
        parser = ALEParser(self.file_name, strict=True)
        self.assertEqual(parser.source_name, self.file_name)

        parser.parse()

        self.assertEqual(digest_data(parser.heading), '048ae109bcba60d3e85c8f5ece9011d8')
        self.assertEqual(digest_data(parser.columns), 'ca25e97621e22bc63d173c2fca7f729d')
        self.assertEqual(digest_data(parser.data), '985d69a6f00745a2528f1df6a478d212')

    def test_filehandle(self):
        parser = ALEParser(self.file_handle)
        self.assertEqual(parser.source_name, self.file_name)

        parser.parse()

        self.assertEqual(digest_data(parser.heading), '048ae109bcba60d3e85c8f5ece9011d8')
        self.assertEqual(digest_data(parser.columns), 'ca25e97621e22bc63d173c2fca7f729d')
        self.assertEqual(digest_data(parser.data), '985d69a6f00745a2528f1df6a478d212')

    def test_stream(self):
        from StringIO import StringIO
        parser = ALEParser()
        stream = StringIO(self.file_text)
        parser.set_source(stream)
        self.assertEqual(parser.source_name, '<stream>')

        parser.set_source(stream, 'this is the filename here')
        self.assertEqual(parser.source_name, 'this is the filename here')

        parser.parse()

        self.assertEqual(digest_data(parser.heading), '048ae109bcba60d3e85c8f5ece9011d8')
        self.assertEqual(digest_data(parser.columns), 'ca25e97621e22bc63d173c2fca7f729d')
        self.assertEqual(digest_data(parser.data), '985d69a6f00745a2528f1df6a478d212')

    def test_text(self):
        parser = ALEParser()
        parser.set_source(self.file_text)
        self.assertEqual(parser.source_name, '<string>')

        parser.set_source(self.file_text, 'this is the filename here')
        self.assertEqual(parser.source_name, 'this is the filename here')

        parser.parse()

        self.assertEqual(digest_data(parser.heading), '048ae109bcba60d3e85c8f5ece9011d8')
        self.assertEqual(digest_data(parser.columns), 'ca25e97621e22bc63d173c2fca7f729d')
        self.assertEqual(digest_data(parser.data), '985d69a6f00745a2528f1df6a478d212')

        file_text = self.file_text.replace('\n', '\r\n')
        parser.set_source(file_text)

        parser.parse()

        self.assertEqual(digest_data(parser.heading), '048ae109bcba60d3e85c8f5ece9011d8')
        self.assertEqual(digest_data(parser.columns), 'ca25e97621e22bc63d173c2fca7f729d')
        self.assertEqual(digest_data(parser.data), '985d69a6f00745a2528f1df6a478d212')


        file_text = self.file_text.replace('\n', '\r')
        parser.set_source(file_text)

        parser.parse()

        self.assertEqual(digest_data(parser.heading), '048ae109bcba60d3e85c8f5ece9011d8')
        self.assertEqual(digest_data(parser.columns), 'ca25e97621e22bc63d173c2fca7f729d')
        self.assertEqual(digest_data(parser.data), '985d69a6f00745a2528f1df6a478d212')

    def test_errors(self):
        with self.assertRaises(ALEError):
            parser = ALEParser(list())

        with self.assertRaises(ALEError):
            parser = ALEParser()
            parser.set_source(list())

        # Missing source
        parser = ALEParser(strict=True)
        with self.assertRaises(ALEError):
            parser.parse()

        # Missing required heading
        parser.set_source(self.file_text.replace('FPS\t29.97', ''))
        with self.assertRaises(ALESyntaxError):
            parser.parse()

        # Missing required column
        parser.set_source(self.file_text.replace('\tEnd\n', '\n'))
        with self.assertRaises(ALESyntaxError):
            parser.parse()

        # Excess heading items
        error_heading = ['FPS\t29.97'] + ['TEST {0}\t{0}'.format(i) for i in range(63)]
        parser.set_source(self.file_text.replace('FPS\t29.97', '\n'.join(error_heading)))
        with self.assertRaises(ALESyntaxError):
            parser.parse()

        # Excess column items
        excess_column = ['End'] + ['Test {0}'.format(i) for i in range(63)]
        parser.set_source(self.file_text.replace('End\n', '\t'.join(excess_column) + '\n'))
        with self.assertRaises(ALESyntaxError):
            parser.parse()

        # Malformed heading declaration
        parser.set_source(self.file_text.replace(
            'VIDEO_FORMAT\tNTSC',
            'VIDEO_FORMAT  NTSC'))
        with self.assertRaises(ALESyntaxError):
            parser.parse()

        # Malformed column declaration
        parser.set_source(self.file_text.replace(
            'Name\tTracks\tStart\tEnd',
            'Name  Tracks  Start  End'))
        with self.assertRaises(ALESyntaxError):
            parser.parse()

        # Columns already defined...
        parser.set_source(self.file_text.replace(
            'Name\tTracks\tStart\tEnd',
            'Name\tTracks\tStart\tEnd\nName\tTracks\tStart\tEnd'))
        with self.assertRaises(ALESyntaxError):
            parser.parse()

        # We cant parse PIZZA delimited files! :O
        parser.set_source(self.file_text.replace('TABS', 'PIZZA'))
        with self.assertRaises(ALESyntaxError):
            parser.parse()

        # Missing sections - no Heading
        parser.set_source(self.file_text.split('Heading', 1)[1])
        with self.assertRaises(ALESyntaxError):
            parser.parse()

        # Missing sections - no Column
        parser.set_source(self.file_text.split('Column', 1)[0])
        with self.assertRaises(ALESyntaxError):
            parser.parse()

        # Missing sections - no Data
        parser.set_source(self.file_text.split('Data', 1)[0])
        with self.assertRaises(ALESyntaxError):
            parser.parse()

def main():
    from test import test_support
    test_support.run_unittest(CheckSimpleALE)

if __name__ == '__main__':
    main()
