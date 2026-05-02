#!/usr/bin/env python3
import sys, subprocess, re

HFST_FILE = '/home/asus/new-eng-bcl/eng-bcl.autogen.hfst'

def normalize_tags(token):
    token = re.sub(r'<v><pres><p3><sg>', '<v><past>', token)
    token = re.sub(r'<v><pres><prog>', '<v><past>', token)
    token = re.sub(r'<v><pres>', '<v><past>', token)
    token = re.sub(r'<v><inf>', '<v><past>', token)
    token = re.sub(r'<v><imp>', '<v><past>', token)
    token = re.sub(r'<v><pp>', '<v><past>', token)
    return token

def process(stream):
    tokens = re.findall(r'\^([^$]+)\$', stream)
    spaces = re.split(r'\^[^$]+\$', stream)
    if not tokens:
        sys.stdout.write(stream)
        return
    normalized = [normalize_tags(t) for t in tokens]
    input_str = '\n'.join(normalized) + '\n'
    result = subprocess.run(
        ['hfst-lookup', '-q', '-O', 'apertium', HFST_FILE],
        input=input_str, capture_output=True, text=True
    )
    outputs = []
    for line in result.stdout.strip().split('\n'):
        if not line.strip():
            continue
        m = re.match(r'\^[^/]+/([^$]+)\$', line)
        if m:
            out = m.group(1)
            if out.startswith('*'):
                outputs.append('#' + out[1:].split('<')[0])
            else:
                outputs.append(out)
        else:
            outputs.append(line)
    output = spaces[0]
    for i, token in enumerate(tokens):
        if i < len(outputs):
            output += outputs[i]
        if i + 1 < len(spaces):
            output += spaces[i + 1]
    sys.stdout.write(output)

data = sys.stdin.read()
process(data)
