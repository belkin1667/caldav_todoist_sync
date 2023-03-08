import urllib.request


def ping(host):
    try:
        contents = urllib.request.urlopen(host).read()
        return True
    except:
        return False
