import os
from os import listdir
from os.path import isfile, join
import random



def randint(n):
    return int(random.random() * n)

def FindAllFiles(mypath):
    return [mypath + '/' + f for f in listdir(mypath) if isfile(join(mypath, f))]


def ReadFileSafe(path, wrapper=""):
    if not isfile(path):
        return wrapper
    f = open(path, 'r')
    data = f.read()
    f.close()
    return data


def ReadTokenFile(path):
        f = open(path, 'r')
        token = f.read()
        f.close()
        return token.strip()


def GetToken(args):
    if args.token:
        return args.token

    if args.token_path:
        return ReadTokenFile(args.token_path)

    if args.token_env:
        return os.environ[args.token_env]

    if not "TELEGRAM_TOKEN" in os.environ:
        print("Args --token, --token-path, --token-env or env var TELEGRAM_TOKEN must be set!")
        exit(-1)

    return os.environ["TELEGRAM_TOKEN"]

