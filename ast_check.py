"""Isolated syntax inspection. Never compile or execute submitted Python."""
import ast, json, sys
try:
    import resource
    resource.setrlimit(resource.RLIMIT_CPU,(2,2))
    resource.setrlimit(resource.RLIMIT_AS,(192*1024*1024,192*1024*1024))
except (ImportError,ValueError):
    pass
source=sys.stdin.read(16001)
try:
    if len(source)>16000: raise ValueError('Too long')
    tree=ast.parse(source)
    counts={'asserts':sum(isinstance(n,ast.Assert) for n in ast.walk(tree)), 'assert_methods':sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr.startswith('assert') for n in ast.walk(tree))}
    print(json.dumps(counts))
except (SyntaxError,ValueError,MemoryError,RecursionError):
    print('{}')
