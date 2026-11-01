"""Static sanity checks for GML source (no GameMaker required).

This is NOT a compiler. It catches the mistakes that are easy to make when GML
is edited outside the IDE: unbalanced brackets, unterminated strings, calls to
undefined project functions, wrong argument counts, misspelled resources,
reads of never-assigned globals and use of undeclared `_local` variables
(project convention: every local starts with an underscore).

Usage: python tools/check_gml.py        (exit code 1 when problems are found)
"""
from pathlib import Path
import re, sys

ROOT = Path(__file__).resolve().parents[1]
PREFIXES = ('obj_', 'spr_', 'snd_', 'rm_', 'fnt_', 'scr_')
TOKEN = re.compile(r'''
    (?P<lc>//[^\n]*) | (?P<bc>/\*.*?\*/) |
    (?P<str>@?"(?:[^"\\\n]|\\.)*") | (?P<str2>'(?:[^'\\\n]|\\.)*') |
    (?P<num>0x[0-9a-fA-F]+|\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+) |
    (?P<id>[A-Za-z_][A-Za-z0-9_]*) |
    (?P<nl>\n) | (?P<ws>[ \t\r]+) | (?P<op>.)
''', re.X | re.S)
PAIRS = {')': '(', ']': '[', '}': '{'}


def tokenize(text, problems, name):
    out, line, pos = [], 1, 0
    while pos < len(text):
        m = TOKEN.match(text, pos)
        if not m:
            problems.append(f'{name}:{line}: cannot tokenize'); break
        kind, val = m.lastgroup, m.group()
        if kind in ('str', 'str2', 'num', 'id', 'op'):
            out.append((kind, val, line))
        line += val.count('\n')
        pos = m.end()
    # an unterminated string shows up as a lone quote character
    for kind, val, ln in out:
        if kind == 'op' and val in '"\'':
            problems.append(f'{name}:{ln}: unterminated string')
    return out


def check_brackets(tokens, problems, name):
    stack = []
    for kind, val, ln in tokens:
        if kind != 'op':
            continue
        if val in '([{':
            stack.append((val, ln))
        elif val in PAIRS:
            if not stack or stack[-1][0] != PAIRS[val]:
                problems.append(f'{name}:{ln}: unexpected {val!r}'); return
            stack.pop()
    for val, ln in stack:
        problems.append(f'{name}:{ln}: unclosed {val!r}')


def param_list(tokens, i):
    """tokens[i] is '(' after `function name`; return [(name, has_default)]."""
    depth, params, cur, j = 0, [], [], i
    while j < len(tokens):
        kind, val, _ = tokens[j]
        if kind == 'op' and val in '([{': depth += 1
        elif kind == 'op' and val in ')]}':
            depth -= 1
            if depth == 0:
                break
        if depth == 1 and kind == 'op' and val == ',':
            params.append(cur); cur = []
        elif not (depth == 1 and kind == 'op' and val == '('):
            cur.append((kind, val))
        j += 1
    if cur: params.append(cur)
    res = []
    for p in params:
        if p and p[0][0] == 'id':
            res.append((p[0][1], any(v == '=' for _, v in p)))
    return res, j


def call_args(tokens, i):
    """tokens[i] is '(' of a call; return the number of top-level arguments."""
    depth, count, seen, j = 0, 0, False, i
    while j < len(tokens):
        kind, val, _ = tokens[j]
        if kind == 'op' and val in '([{': depth += 1
        elif kind == 'op' and val in ')]}':
            depth -= 1
            if depth == 0: break
        elif depth == 1 and kind == 'op' and val == ',': count += 1
        if depth >= 1 and not (depth == 1 and kind == 'op' and val == '('):
            seen = True
        j += 1
    return (count + 1 if seen else 0)


def declared_locals(tokens):
    names = set()
    for i, (kind, val, _) in enumerate(tokens):
        if kind == 'id' and val == 'function':
            j = i + 1
            if j < len(tokens) and tokens[j][0] == 'id': j += 1
            if j < len(tokens) and tokens[j][1] == '(':
                ps, _ = param_list(tokens, j)
                names.update(p for p, _ in ps)
        if kind == 'id' and val == 'catch' and i + 2 < len(tokens) and tokens[i+1][1] == '(' and tokens[i+2][0] == 'id':
            names.add(tokens[i+2][1])
        if kind == 'id' and val == 'var':
            j, depth = i + 1, 0
            expect = True
            while j < len(tokens):
                k, v, _ = tokens[j]
                if k == 'op' and v in '([{': depth += 1
                elif k == 'op' and v in ')]}':
                    if depth == 0: break
                    depth -= 1
                elif depth == 0 and k == 'op' and v == ';': break
                elif depth == 0 and k == 'op' and v == ',': expect = True; j += 1; continue
                elif depth == 0 and k == 'id' and expect:
                    names.add(v); expect = False
                j += 1
    return names


def main():
    problems, warnings = [], []
    yyp = (ROOT / 'Wall Protocol.yyp').read_text(encoding='utf-8-sig')
    resources = set(re.findall(r'"name":"([A-Za-z0-9_]+)"', yyp)) | {'Room1'}
    files = sorted(p for p in ROOT.rglob('*.gml') if 'build' not in p.parts)
    parsed = {}
    for p in files:
        rel = str(p.relative_to(ROOT))
        text = p.read_text(encoding='utf-8')
        if '\r' in text: problems.append(f'{rel}: CRLF line endings (project uses LF)')
        toks = tokenize(text, problems, rel)
        check_brackets(toks, problems, rel)
        parsed[rel] = toks

    funcs, macros, global_writes = {}, set(), set()
    for rel, toks in parsed.items():
        for i, (k, v, ln) in enumerate(toks):
            if k == 'id' and v == 'function' and i + 2 < len(toks) and toks[i+1][0] == 'id' and toks[i+2][1] == '(':
                ps, _ = param_list(toks, i + 2)
                if toks[i+1][1] in funcs: problems.append(f'{rel}:{ln}: duplicate function {toks[i+1][1]}')
                funcs[toks[i+1][1]] = (sum(1 for _, d in ps if not d), len(ps))
    for p in files:
        for m in re.finditer(r'^#macro\s+(\w+)', p.read_text(encoding='utf-8'), re.M): macros.add(m.group(1))
    for rel, toks in parsed.items():
        for i in range(len(toks) - 3):
            if toks[i][1] == 'global' and toks[i+1][1] == '.' and toks[i+2][0] == 'id':
                nxt = toks[i+3][1]
                if nxt in ('=', '+', '-', '*', '/', '|', '&', '^') or (nxt == '[' ) or nxt == '.' or nxt == '+':
                    global_writes.add(toks[i+2][1])
    palette = set(re.findall(r'(\w+):make_color_rgb', (ROOT / 'scripts/scr_config/scr_config.gml').read_text(encoding='utf-8')))
    for rel, toks in parsed.items():
        for i in range(len(toks) - 4):
            if toks[i][1] == 'global' and toks[i+2][1] == 'col' and toks[i+3][1] == '.' and toks[i+4][0] == 'id':
                if toks[i+4][1] not in palette:
                    problems.append(f'{rel}:{toks[i][2]}: unknown palette colour global.col.{toks[i+4][1]}')

    for rel, toks in parsed.items():
        is_script = rel.startswith('scripts/')
        # scope handling: scripts are checked per top-level function, events per file
        scopes, cur, depth, start = [], [], 0, 0
        if is_script:
            i = 0
            while i < len(toks):
                if toks[i][1] == 'function' and depth == 0:
                    j = i
                    while j < len(toks) and toks[j][1] != '{': j += 1
                    d = 0
                    while j < len(toks):
                        if toks[j][1] == '{': d += 1
                        elif toks[j][1] == '}':
                            d -= 1
                            if d == 0: break
                        j += 1
                    scopes.append(toks[i:j + 1]); i = j + 1
                else:
                    i += 1
        else:
            scopes = [toks]
        for scope in scopes:
            names = declared_locals(scope)
            for i, (k, v, ln) in enumerate(scope):
                prev = scope[i-1][1] if i else ''
                nxt = scope[i+1][1] if i + 1 < len(scope) else ''
                if k != 'id' or prev == '.':
                    continue
                if v.startswith('_') and not v.startswith('__') and v not in names and nxt != ':':
                    problems.append(f'{rel}:{ln}: local {v} used but never declared')
                if v.startswith('wp_') and nxt == '(' and prev != 'function':
                    if v not in funcs: problems.append(f'{rel}:{ln}: call to undefined function {v}')
                    else:
                        n = call_args(scope, i + 1)
                        lo, hi = funcs[v]
                        if not lo <= n <= hi: problems.append(f'{rel}:{ln}: {v} called with {n} args (expects {lo}..{hi})')
                if v.startswith(PREFIXES) and nxt != '(' and prev != 'function':
                    if v not in resources and v not in funcs: problems.append(f'{rel}:{ln}: unknown resource {v}')
                if prev == '.' :
                    continue
        for i in range(len(scope := toks) - 2):
            if toks[i][1] == 'global' and toks[i+1][1] == '.' and toks[i+2][0] == 'id':
                g = toks[i+2][1]
                if g not in global_writes:
                    problems.append(f'{rel}:{toks[i][2]}: global.{g} is read but never assigned')
    for p in sorted(set(problems)): print('PROBLEM', p)
    print(f'{len(files)} GML files, {len(funcs)} project functions, {len(macros)} macros checked: '
          + ('OK' if not problems else f'{len(set(problems))} problem(s)'))
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
