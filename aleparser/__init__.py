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

# Simple ALE Parser based on Avid Log Specification Appendix C
# - http://www.24p.com/PDF/ALE_Spec.pdf
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class ALEError(Exception): pass
class ALESyntaxError(ALEError): pass


class ALEParser(object):
    """
    parser = ALEParser()
    
    parser.set_source('filename.ALE') or
    parser.set_source(<String containing ALE contents>, 'filename.ALE')
    parser.set_source(io.stream, 'filename.ALE')

    parser.parse()
    
    print parser.heading
    print parser.columns
    print parser.data
    """

    def __init__(self, source=None, source_name=None, strict=False):
        self.strict = strict
        if source is not None:
            self.set_source(source, source_name)
        else:
            self.source = None
            self.source_name = None

            self._state = 0
            self._lineno = 0
            self._line = ''
            self._sline = ''

            self.heading = {}
            self.columns = []
            self.data = []

    def set_source(self, source, source_name=None):
        if isinstance(source, (str, unicode)):
            if '\n' in source or '\r' in source:
                # Fix newlines...
                if '\r\n' in source or '\n\r' in source:
                    source = source.replace('\r\n', '\n').replace('\n\r', '\n')
                if '\r' in source:
                    source = source.replace('\r', '\n')

                self.source = StringIO(source)

                if source_name is not None:
                    self.source_name = source_name
                else:
                    self.source_name = '<string>'
            else:
                # Read in universal line mode
                self.source = open(source, 'rU')
                self.source_name = source

        elif hasattr(source, 'read') and hasattr(source, '__iter__'):
            self.source = source

            if source_name is not None:
                self.source_name = source_name
            elif hasattr(source, 'name'):
                self.source_name = source.name
            else:
                self.source_name = '<stream>'
        else:
            raise ALEError('Unsupported source value')


        self._state = 0
        self._lineno = 0
        self._line = ''
        self._sline = ''

        self.heading = {}
        self.columns = []
        self.data = []

    def _SyntaxError(self, error):
        return ALESyntaxError(
            '<{0!r}:{1:03d}> {2}'.format(self.source_name, self._lineno, error))

    def _check_headings(self):
        # Required headings according to the specification
        for req_heading in ('FIELD_DELIM', 'VIDEO_FORMAT', 'TAPE', 'FPS'):
            if req_heading not in self.heading:
                raise self._SyntaxError(
                    'Missing required {0} heading'.format(req_heading))

        if len(self.heading) > 64:
            raise self._SyntaxError("Heading has more than 64 fields defined!")
        
        # Possible TODO: include more strict key/value checks

    def _check_columns(self):
        # Require columns according to the specification...
        for req_column in ('Name', 'Tracks', 'Start', 'End'):
            if req_column not in self.columns:
                raise self._SyntaxError(
                    'Missing required {0} column'.format(req_column))

        if len(self.columns) > 64:
            raise self._SyntaxError("Column has more than 64 columns defined!")

    def parse(self):
        if self.source is None:
            raise ALEError('Source not set, use set_source first!')

        STATE_INIT, STATE_HEADING, STATE_COLUMN, STATE_DATA = (0, 1, 2, 3)

        self._state = STATE_INIT
        self._lineno = 0

        self.heading = {}
        self.columns = []
        self.rows = []

        for line in self.source:
            self._lineno += 1
            self._line = line.rstrip('\n')
            self._sline = line.strip()

            if self._state == STATE_INIT:
                # Do nothing until we see Heading
                if self._sline == 'Heading':
                    self._state = STATE_HEADING
                else:
                    pass
                # Do nothing
                continue

            elif self._state == STATE_HEADING:
                # Parse the Heading
                if self._sline == 'Column':
                    if self.strict:
                        self._check_headings()

                    self._state = STATE_COLUMN
                elif self._sline != '':
                    self._parse_heading()
                continue

            elif self._state == STATE_COLUMN:
                # Parse the Column
                if self._sline == 'Data':
                    if self.strict:
                        self._check_columns()
                    self._state = STATE_DATA

                elif self._sline != '':
                    self._parse_column()
                continue

            elif self._state == STATE_DATA:
                # Parse data, skip blank lines
                if self._sline != '':
                    self._parse_data()
                continue

            raise self._SyntaxError(
                'Unexpected error occured in parsing document')

        if self._state != STATE_DATA:
            errors = ('Heading', 'Columns', 'Data')
            raise self._SyntaxError(
                'Malformed ALE file missing {0} section'.format(errors[self._state]))

    def _parse_heading(self):
        if self._line.count('\t') != 1:
            raise self._SyntaxError('Malformed heading section')

        key, value = map(str.strip, self._line.split('\t'))
        if key == 'FIELD_DELIM':
            if value != 'TABS':
                raise self._SyntaxError('Unable to handle non tab delimited ALE files')

        self.heading[key] = value

    def _parse_column(self):
        if len(self.columns) != 0:
            raise self._SyntaxError('Columns already defined')

        if '\t' not in self._line:
            raise self._SyntaxError('Malformed column definition')

        self.columns = map(str.strip, self._line.split('\t'))

    def _parse_data(self):
        if self._line.count('\t') != len(self.columns)-1:
            raise self._SyntaxError('Malformed data line')

        # Could write this neater, but it works...
        self.data.append(dict(zip(self.columns, map(str.strip, self._line.split('\t')))))
