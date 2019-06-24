import re

raw_pattern = re.compile(r'<[^>]+>')
part_lookup = {
    'show': '(?P<show>[A-Za-z_0-9]+)',
    'season': '(?P<season>[0-9]+)',
    'episode': '(?P<episode>[0-9]+)',
}


def compile_pattern(s: str):
    pass
    """
    anything not in <> is getting escaped, anything like <$...> is getting special treatment 
    """
    # todo this doesn't handle nested <> statements
    parts = []
    ind = 0
    while ind < len(s):
        next_raw = raw_pattern.search(s, ind)
        if not next_raw:
            parts.append(s[ind:])
            break
        parts.append(s[ind: next_raw.start(0)])
        parts.append(s[next_raw.start(0): next_raw.end(0)])
        ind = next_raw.end(0)

    ret = []
    for part in parts:
        if part.startswith('<$'):
            part_id = part[2:-1]
            ret.append(part_lookup[part_id])
        elif part.startswith('<'):
            part_raw = part[1:-1]
            ret.append(part_raw)
        else:
            ret.append(re.escape(part))
    return re.compile(''.join(ret)+'$')
