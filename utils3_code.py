import sys

from utils3.data.encode import *

argv = sys.argv

if len(argv) > 1:
    data = argv[1].encode()
    detector.check(data)
else:
    print('usage: *.py string_data')
