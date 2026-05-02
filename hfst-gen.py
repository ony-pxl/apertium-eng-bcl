#!/usr/bin/env python3
import sys, subprocess, re

HFST_FILE = sys.argv[1] if len(sys.argv) > 1 else '/home/asus/new-eng-bcl/eng-bcl.autogen.hfst'

BARE_VERBS = {'padaba'}

def normalize_tags(token):
    lem = token.split('<')[0]
    if lem in BARE_VERBS:
        return f'__BARE__{lem}'
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

    # Check for padaba + ako + ika pattern → padaba taka
    # Replace the whole stream before processing
    new_tokens = []
    i = 0
    skip_indices = set()
    while i < len(tokens):
        t = tokens[i]
        lem = t.split('<')[0]
        if (lem == 'padaba' and
            i+1 < len(tokens) and tokens[i+1].split('<')[0] == 'ako' and
            i+2 < len(tokens) and tokens[i+2].split('<')[0] == 'ika'):
            new_tokens.append('__LITERAL__padaba taka')
            skip_indices.add(i+1)
            skip_indices.add(i+2)
            i += 3
            continue
        new_tokens.append(t)
        i += 1

    normalized = [normalize_tags(t) if not t.startswith('__LITERAL__') else t
                  for t in new_tokens]

    # Run hfst on non-bare, non-literal tokens
    hfst_inputs = []
    hfst_map = {}
    outputs = {}

    for i, t in enumerate(normalized):
        if t.startswith('__BARE__'):
            outputs[i] = t.replace('__BARE__', '')
        elif t.startswith('__LITERAL__'):
            outputs[i] = t.replace('__LITERAL__', '')
        else:
            hfst_map[len(hfst_inputs)] = i
            hfst_inputs.append(t)

    if hfst_inputs:
        input_str = '\n'.join(hfst_inputs) + '\n'
        result = subprocess.run(
            ['hfst-lookup', '-q', '-O', 'apertium', HFST_FILE],
            input=input_str, capture_output=True, text=True
        )
        lines = [l for l in result.stdout.strip().split('\n') if l.strip()]
        for j, line in enumerate(lines):
            if j in hfst_map:
                idx = hfst_map[j]
                m = re.match(r'\^[^/]+/([^$]+)\$', line)
                if m:
                    out = m.group(1)
                    outputs[idx] = '#' + out[1:].split('<')[0] if out.startswith('*') else out
                else:
                    outputs[idx] = line

    # Reconstruct — use original spaces but new token count
    output = spaces[0]
    for i in range(len(new_tokens)):
        output += outputs.get(i, new_tokens[i].split('<')[0])
        if i + 1 < len(spaces):
            output += spaces[i + 1]

    sys.stdout.write(output)

data = sys.stdin.read()
process(data)
