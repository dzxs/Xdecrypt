import os
import sys
import argparse
import base64
import configparser

from win32api import GetComputerName, GetUserName
from win32security import LookupAccountName, ConvertSidToStringSid
from Crypto.Hash import SHA256
from Crypto.Cipher import ARC4


def decrypt_string(a1, a2):
    v1 = base64.b64decode(a2)
    v3 = ARC4.new(SHA256.new(a1.encode('ascii')).digest()).decrypt(v1[:len(v1) - 0x20])
    if SHA256.new(v3).digest() == v1[-32:]:
        return v3.decode('ascii')
    else:
        return None

VERSION_6_CONFIG_PATH = os.path.join(os.environ["USERPROFILE"], r"Documents\NetSarang Computer\6")
VERSION_7_CONFIG_PATH = os.path.join(os.environ["USERPROFILE"], r"Documents\NetSarang Computer\7")

config_path = ""
parser = argparse.ArgumentParser(description="xsh, xfp password decrypt")
parser.add_argument("-u", "--user", default="", type=str, help="`username`,`whoami` in command.")
parser.add_argument("-s", "--sid", default="", type=str, help="`sid`,`whoami /user` in command.")
parser.add_argument("-p", "--password", default="", type=str, help="the password in sessions or path of sessions")
args = parser.parse_args()

if not args.password:
    if os.path.exists(VERSION_6_CONFIG_PATH):
        config_path = VERSION_6_CONFIG_PATH
    elif os.path.exists(VERSION_7_CONFIG_PATH):
        config_path = VERSION_7_CONFIG_PATH
    else:
        print("Error: can't found valid session path")
        sys.exit(0)    
    args.password = config_path

if not args.sid:
    # method from https://github.com/JDArmy/SharpXDecrypt
    if config_path == VERSION_7_CONFIG_PATH:
        tmp = GetUserName()[::-1] + ConvertSidToStringSid(LookupAccountName(GetComputerName(), GetUserName())[0])
        args.sid = tmp[::-1]
    else:
        args.sid = GetUserName() + ConvertSidToStringSid(LookupAccountName(GetComputerName(), GetUserName())[0])

if not os.path.isdir(args.password):
    r = decrypt_string(args.sid[::-1]+args.user, args.password)
    if r:
        print(r)

for root, dirs, files in os.walk(args.password):
    for f in files:
        if f.endswith(".xsh") or f.endswith(".xfp"):
            filepath = os.path.join(root, f)
            cfg = configparser.ConfigParser()
            try:
                cfg.read(filepath)
            except UnicodeDecodeError:
                cfg.read(filepath, encoding="utf-16")
            try:
                if f.endswith(".xsh"):
                    host = "{}:{}".format(cfg["CONNECTION"]["Host"], cfg["CONNECTION"]["Port"])
                    username = cfg["CONNECTION:AUTHENTICATION"]["UserName"]
                    password = decrypt_string(args.sid, cfg["CONNECTION:AUTHENTICATION"]["Password"])
                else:
                    host = "{}:{}".format(cfg["Connection"]["Host"], cfg["Connection"]["Port"])
                    username = cfg["Connection"]["UserName"]
                    password = decrypt_string(args.sid, cfg["Connection"]["Password"])
                print(args.sid)
                print(cfg["CONNECTION:AUTHENTICATION"]["Password"])
                print(
                    f"{filepath:=^100}\nHost:     {host}\nUsername: {username}\nPassword: {password}")
            except Exception as e:
                print(f"{filepath:=^100}\nError:{e}")
