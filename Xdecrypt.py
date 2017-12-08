import argparse
import base64
from Crypto.Hash import SHA256
from Crypto.Cipher import ARC4


def decrypt_string(a1, a2):
    v1 = base64.b64decode(a2)
    v3 = ARC4.new(SHA256.new(a1.encode('ascii')).digest()).decrypt(v1[:len(v1)-0x20])
    if SHA256.new(v3).digest() == v1[-32:]:
        return v3.decode('ascii')
    else:
        return None


parser = argparse.ArgumentParser(description="xsh, xfp password decrypt")
parser.add_argument("sid", type=str, help="`username`+`sid`, use `whoami /user` in command")
parser.add_argument("password", type=str, help="the password in sessions")

args = parser.parse_args()
r = decrypt_string(args.sid, args.password)
if r:
    print(r)
