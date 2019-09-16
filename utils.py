def service_paths_to_tree(services):
    #A simple recursion will do -- they said
    #https://codegolf.stackexchange.com/a/4485
    def build_nested_helper(path, service, container):
        segs = path
        head = segs[0]
        tail = segs[1:]
        if not tail:
            container.append({
                "text": "%s [%s]%s" % (service.tag, service.original_url, service.via and " (via %s)" % service.via.tag or ''),
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
        for path in paths:
            build_nested_helper(path[0], path[1], container)
        return container
    return build_nested(services)

def traverse(obj, path=None, callback=None):
    if path is None:
        path = []

    if isinstance(obj, dict):
        #if '_type' in obj:
        #    return obj['_type']
        value = {k: traverse(v, path + [k], callback)
                 for k, v in obj.items()}
    elif isinstance(obj, list):
        value = [traverse(elem, path + [[]], callback)
                 for elem in obj]
    else:
        value = obj

    if callback is None:
        return value
    else:
        return callback(path, value)


