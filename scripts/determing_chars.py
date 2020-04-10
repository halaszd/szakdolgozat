import unicodedata


def write(outp):
    with open('chars_with_unicode_name.txt', 'w', encoding='utf-8') as f:
        for key, value in outp.items():
            print(key + '\t', value, file=f)


def read(inp):
    with open(inp, 'r', encoding='utf-8') as f:
        return f.read().replace('(', '').replace(')', '').replace('|', '\n')


def process(inp):
    char_dict = {}
    for i, s in enumerate(inp.split('\n')):
        if s.strip() != '':
            char_nms = []
            for char in s:
                char_nms.append(unicodedata.name(char))
            char_dict[s] = ' + '.join(char_nms)
    return char_dict


def main():
    fpath = 'chars.txt'
    inp = read(fpath)
    outp = process(inp)
    write(outp)


if __name__ == '__main__':
    main()
