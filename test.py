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


from aleparser import ALEParser

def main():
    from pprint import pprint
    sample_ALE = """Heading
FIELD_DELIM	TABS
VIDEO_FORMAT	NTSC
AUDIO_FORMAT	44kHz
TAPE	001
FPS	29.97
Column
Name	Tracks	Start	End
Data
CU Josh & Mary	V	01:00:00:00	01:15:05:00"""

    parser = ALEParser(strict=True)
    parser.set_source(sample_ALE, 'sample.ALE')
    parser.parse()

    pprint(parser.heading)
    pprint(parser.columns)
    pprint(parser.data)

    # from http://www.24p.com/ALE.htm
    parser.set_source('all_headings.ALE')
    parser.parse()

    pprint(parser.heading)
    pprint(parser.columns)
    pprint(parser.data)


if __name__ == '__main__':
    main()