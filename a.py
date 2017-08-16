# Python Version: 2.x
# -*- coding: utf-8 -*-
import clang.cindex
from clang.cindex import Index
from clang.cindex import Config
import re
import sys
import yaml
from collections import OrderedDict

def log_info(msg, *args):
    sys.stderr.write((msg % args) + '\n')

def list_or_singleton(x):
    if isinstance(x, list):
        return x
    else:
        return [ x ]

def yaml_ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)

def load_identifier_table(s):
    return yaml_ordered_load(s)

def get_undeclared_identifiers(code):
    index = Index.create()
    tu = index.parse('<stdin>.cpp', unsaved_files=[ ('<stdin>.cpp', code) ], args=[ '-std=c++14' ])
    undeclared_identifiers = []
    for diag in tu.diagnostics:
        log_info('%s', diag.format())
        m = re.match(r"^no member named '(.*)' in namespace '(.*)'$", diag.spelling)
        if m:
            ident = m.group(2) + '::' + m.group(1)
            log_info('[*] undefined identifier found: %s', ident)
            undeclared_identifiers += [ ident ]
        m = re.match(r"^use of undeclared identifier '(.*)'$", diag.spelling)
        if m:
            ident = m.group(1)
            log_info('[*] undefined identifier found: %s', ident)
            undeclared_identifiers += [ ident ]
    return sorted(set(undeclared_identifiers))

def construct_header(undefined, table, code):
    undefined = set(undefined)
    result = []
    used = set()
    def require(ident, result=result, used=used):
        # nonlocal result  # Python 2.x has no nonlocal keyword
        if ident in used:
            return
        used.add(ident)
        log_info('[*] definition of identifier required: %s', ident)
        descr = table[ident]
        if isinstance(descr, str):
            result += [ descr ]
        else:
            for key, value in descr.items():
                if key == 'require':
                    for it in list_or_singleton(value):
                        require(it)
                elif key == 'namespace':
                    result += [ 'using namespace %s;' % value ]
                    log_info('[*] using namespace %s', value)
                    require(value + '::' + ident)
                elif key == 'string':
                    result += [ value ]
                elif key == 'file':
                    with open(value) as fh:
                        result += [ fh.read() ]
                elif key == 'grep':
                    pass
                else:
                    assert False
    for ident in table:
        if ident in undefined:
            require(ident)
        if isinstance(table[ident], dict) and table[ident].get('grep'):
            if ident in code:
                require(ident)
    return sorted(set(result))

def remove_unnecessary_lines(xs, code):
    lines = set(map(lambda line: line.rstrip(), code.splitlines()))
    ys = []
    for x in xs:
        if x not in lines:
            ys += [ x ]
    return ys

def order_lines(xs):
    include = []
    define = []
    using_namespace = []
    other = []
    for x in xs:
        if x.startswith('#include'):
            include += [ x ]
        elif x.startswith('#define'):
            define += [ x ]
        elif x.startswith('using namespace '):
            using_namespace += [ x ]
        else:
            other += [ x ]
    return include + define + using_namespace + other

def main():
    import os
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?')
    parser.add_argument('-i', '--in-place', action='store_true')
    parser.add_argument('-x', action='append', dest='options')
    parser.add_argument('--config', default=os.path.join(os.environ['HOME'], '.local', 'share', 'autoinclude', 'config.yaml'))
    args = parser.parse_args()
    if args.options is None:
        args.options = [ '-std=c++14' ]

    with open('default.yaml') as fh:
        table = load_identifier_table(fh.read())
    if os.path.exists(args.config):
        with open(args.config) as fh:
            table.update(load_identifier_table(fh.read()))
    if args.file is None:
        code = sys.stdin.read()
    else:
        with open(args.file) as fh:
            code = fh.read()

    newline = ('\r\n' in code) and '\r\n' or '\n'
    header = []
    for _ in range(10):
        new_code = newline.join(header + [ code ])
        identifiers = get_undeclared_identifiers(new_code)
        new_header = construct_header(identifiers, table, new_code)
        new_header = remove_unnecessary_lines(new_header, new_code)
        new_header = order_lines(set(new_header + header))
        if len(new_header) == len(header):
            break
        header = new_header
    header = newline.join(header) + newline

    if args.in_place:
        with open(args.file, 'w') as fh:
            fh.write(header + code)
    else:
        sys.stdout.write(header)

if __name__ == '__main__':
    main()
