import hashlib
import base64
import zlib
import os
import datetime

store_dir = "store"
obj_dir   = os.path.join(store_dir, "objects")
head_file = os.path.join(store_dir, "HEAD")

# returns a base64-encoded string of the hash
def hash_data(data):
    hash_ob = hashlib.sha256(data)
    digest = hash_ob.digest()
    hashstr = base64.b64encode(digest).decode('utf-8')
    hashstr = hashstr.replace("+", "-")
    hashstr = hashstr.replace("/", "_")
    hashstr = hashstr.replace("=", ".")
    return hashstr

# takes a hash and returns the path that the content corresponding to that
# hash will be written to. the path is relative to obj_dir
def make_rel_hash_path(h):
    return os.path.join(h[:2], h[2:])

# takes a hash and returns the path to the file in the object store, relative
# to current directory
def path_to_obj(h):
    return os.path.join(obj_dir, make_rel_hash_path(h))

# store needs to be initted before calling this
def write_data(data):
    da_hash = hash_data(data)
    fpath = path_to_obj(da_hash)
    os.makedirs(os.path.dirname(fpath))
    with open(fpath, 'wb') as f:
        f.write(zlib.compress(data))
        f.close()

    return da_hash

def read_data(h):
    with open(path_to_obj(h), 'rb') as f:
        content = f.read()
        return zlib.decompress(content)


def init_store():
    if not os.path.exists(obj_dir):
        os.makedirs(obj_dir)

    if not os.path.exists(head_file):
        open(head_file, 'a').close()


def now_string():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Returns the bytes for a page revision object. It will look like this:
#
#   datetime <date and time of revision>
#   prev <hash of previous page revision object or empty if this is the initial revision>
#   title <hash of page title>
#   <hash of card #1>
#   <hash of card #2>
#   ...
#
# rev_dt: a datetime string,
# prev: hash of previous revision
# title: hash of the page title,
# cards: list of hashes of card content
def page_revision_obj(rev_dt, prev, title, cards):
    s = "datetime {}\nprev {}\ntitle {}\n".format(rev_dt, prev, title)

    for c in cards:
        s += "{}\n".format(c)

    return bytes(s, 'utf-8')


# Returns the bytes for a web state object. It will look like this:
#
#   datetime <date and time the state was created>
#   prev <hash of previous state object or empty if this is initial state>
#   page <hash of page #1>
#   tag <hash of tag #1 for page #1>
#   tag <hash of tag #2 for page #1>
#   ...
#   page <hash of page #2>
#   tag <hash of tag #1 for page #2>
#   tag <hash of tag #2 for page #2>
#   ...
#   ...
#
# create_dt: a datetime string
# prev: hash of previous state
# tagged_pages: list of pairs where first component is hash of page revision
#               and second component is list of hash of tags
def web_state_obj(create_dt, prev, tagged_pages):
    s = "datetime {}\nprev {}\n".format(create_dt, prev, title)

    for p in tagged_pages:
        s += "page{}\n".format(p[0])
        for t in p[1]:
            s += "tag{}\n".format(t)

    return bytes(s, 'utf-8')
