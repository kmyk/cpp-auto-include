# Python Version: 2.x
import yaml

inclusion_filter = {
    'istream': 'iostream',
    'ostream': 'iostream',
    'ios': 'iostream',
    'streambuf': 'iostream',
    'iosfwd': 'ios',
    'initializer_list': 'utility',
    'stddef.h': 'cstddef',
    'limits.h': 'climits',
    'float.h': 'cfloat',
    'stdint.h': 'cstdint',
    'iso646.h': 'ciso646',
    'signal.h': 'csignal',
    'setjmp.h': 'csetjmp',
    'stdalign.h': 'cstdalign',
    'stdarg.h': 'cstdarg',
    'stdbool.h': 'cstdbool',
    'stdlib.h': 'cstdlib',
    'time.h': 'ctime',
    'assert.h': 'cassert',
    'errno.h': 'cerrno',
    'stdlib.h': 'cstdlib',
    'string.h': 'cstring',
    'time.h': 'ctime',
    'ctype.h': 'cctype',
    'wctype.h': 'cwctype',
    'string.h': 'cstring',
    'wchar.h': 'cwchar',
    'stdlib.h': 'cstdlib',
    'uchar.h': 'cuchar',
    'odecvt.h': 'codecvt',
    'locale.h': 'clocale',
    'stdlib.h': 'cstdlib',
    'fenv.h': 'cfenv',
    'math.h': 'cmath',
    'tgmath.h': 'ctgmath',
    'stdlib.h': 'cstdlib',
    'stdio.h': 'cstdio',
    'inttypes.h': 'cinttypes',
}
def generate(x):
    x = yaml.load(x)
    y = {}
    all_idents = set(sum(map(lambda idents: idents or [], x.values()), []))
    for header, idents in x.items():
        for ident in idents or []:
            y[ident] = '#include <%s>' % inclusion_filter.get(header, header)
            if '::' in ident:
                for i in range(1, len(ident.split('::'))):
                    dirname  = '::'.join(ident.split('::')[: i])
                    basename = '::'.join(ident.split('::')[i :])
                    if basename not in all_idents:
                        y[basename] = { 'namespace': dirname }
    return yaml.dump(y, default_flow_style=False)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    import sys
    sys.stdout.write(generate(sys.stdin.read()))
