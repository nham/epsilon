import hashlib
import base64
import zlib
import os

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
    f = open(fpath, 'wb')
    f.write(zlib.compress(data))
    f.close()
    return da_hash

def read_data(h):
    f = open(path_to_obj(h), 'rb')
    content = f.read()
    f.close()
    return zlib.decompress(content)


def init_store():
    if not os.path.exists(obj_dir):
        os.makedirs(obj_dir)

    if not os.path.exists(head_file):
        open(head_file, 'a').close()
