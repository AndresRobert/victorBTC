from datetime import datetime


def info(text):
    print("[{}]|{}".format(datetime.now(), text))


def warn(text):
    print("\033[93m[{}]|{}\033[0m".format(datetime.now(), text))


def error(text):
    print("\033[91m[{}]|{}\033[0m".format(datetime.now(), text))


def success(text):
    print("\033[92m[{}]|{}\033[0m".format(datetime.now(), text))
