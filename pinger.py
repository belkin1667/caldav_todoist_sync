import urllib.request


def ping(host):
    if host is None or host == "":
        return True
    try:
        contents = urllib.request.urlopen(host).read()
        return True
    except:
        return False
