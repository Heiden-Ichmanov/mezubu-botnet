from hashlib import sha256
from sys import argv

if len(argv) == 2:
	print(sha256(argv[1].encode('utf-8')).hexdigest())
