from os import makedirs
from os.path import expanduser
from os import walk, path
from shutil import rmtree
from os import listdir, unlink


def cleanup_dir(target):
    for root, dirs, files in walk(target, topdown=False):
        for name in dirs:
            try:
                pass
                rmtree(path.join(root, name))
            except OSError as e:
                print("Ran into an exception during removal of %s: '%s'" % (path.join(root, name), e))


def cleanup_files(folder):
    for the_file in listdir(folder):
        file_path = path.join(folder, the_file)
        if not path.islink(file_path) and path.isfile(file_path):
            pass
            unlink(file_path)


def makedir_getfd(target):
    target = expanduser(target)
    makedirs(target[:target.rindex('/')], exist_ok=True)
    return open(target, 'w')


def service_paths_to_tree(services):
    #A simple recursion will do -- they said
    #https://codegolf.stackexchange.com/a/4485
    def build_nested_helper(path, service, container):
        segs = path
        head = segs[0]
        tail = segs[1:]
        if not tail:
            container.append({
                "text": "%s [%s]%s" % (service.tag, service.original_url,
                    service.via and " (via %s)" % service.via.tag or ''),
                "type": "website",
                "a_attr": {
                    "href": service.url
                }
            })
        else:
            #folder = {'service':head,'children': []}
            for item in container:
                if item['text'] == head:
                    build_nested_helper(tail, service, item['children'])
                    break
            else:
                folder = {
                    "type": "leaf",
                    "text": head,
                    "children": []
                }
                container.append(folder)
                build_nested_helper(tail, service, folder['children'])

    def build_nested(paths):
        container = []
        for item in paths:
            build_nested_helper(item[0], item[1], container)
        return container
    return build_nested(services)


def traverse(obj, item=None, callback=None):
    if item is None:
        item = []

    if isinstance(obj, dict):
        #if '_type' in obj:
        #    return obj['_type']
        value = {k: traverse(v, item + [k], callback)
                 for k, v in obj.items()}
    elif isinstance(obj, list):
        value = [traverse(elem, item + [[]], callback)
                 for elem in obj]
    else:
        value = obj

    if callback is None:
        return value
    else:
        return callback(item, value)


