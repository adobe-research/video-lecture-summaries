import sys
import os

f = open(str(sys.argv[1]))
contents = f.read()
f.close()
new_contents = contents.replace('\n', ' ')
f = open(str(sys.argv[2]), 'w+')
f.write(new_contents)
f.close()