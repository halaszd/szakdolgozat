import unicodedata
from glob import glob
from collections import defaultdict
import re


def write(outp_1, outp_2):
    with open('../szakdogahoz/chars_with_unicode_name.txt', 'w', encoding='utf-8') as f:
        for elem in outp_1:
            print(elem[0] + '\t', elem[1], file=f)
    with open('../szakdogahoz/chars_in_words.txt', 'w', encoding='utf-8') as f:
        for elem in outp_2:
            print(elem[0] + '\t', ','.join(elem[1]), file=f)


def read(inp):
    for fl in inp:
        with open(fl, 'r', encoding='utf-8') as f:
            yield f.read()


def find_combchars(s, chars_dict, char_in_words):
    pat_space = re.compile(r'\s+')
    is_prev_comb = False
    # to_replace = []
    s = s.split(' ')
    for i, seq in enumerate(s):
        for j, char in enumerate(seq):
            try:
                unicodedata.name(char)
            except ValueError:
                continue
            if unicodedata.combining(char) or 'MODIFIER' in unicodedata.name(char):
                try:
                    if is_prev_comb:
                        chars_dict[seq[j-2:j]+char] = ' + '.join([unicodedata.name(char) for char in seq[j-2:j]+char])
                        if len(char_in_words[seq[j-2:j]+char]) < 11:
                            char_in_words[seq[j-2:j]+char].append(pat_space.sub('', seq))
                    else:
                        chars_dict[seq[j-1]+char] = ' + '.join([unicodedata.name(char) for char in seq[j-1]+char])
                        if len(char_in_words[seq[j-1]+char]) < 11:
                            char_in_words[seq[j-1]+char].append(pat_space.sub('', seq))
                    is_prev_comb = True
                except ValueError:
                    continue
            else:
                chars_dict[char] = unicodedata.name(char)
                is_prev_comb = False
            if len(char_in_words[char]) < 11:
                char_in_words[char].append(pat_space.sub('', seq))


def process(inp):
    combchar_dict = {}
    char_in_words = defaultdict(lambda: [])
    for txt in inp:
        find_combchars(txt, combchar_dict, char_in_words)
    # szótár, amiben key=karakter és value=karakternév, ha combine-olt, akkor a teljes név
    res = sorted(combchar_dict.items(), key=lambda item: item[0])
    # szótár, amiben key=karakter és value=max 10 db szó a listában, ami tartalmazza a karaktert
    res2 = sorted(char_in_words.items(), key=lambda item: item[0])
    print(res2)
    return res, res2


def main():
    fpath = '../betuhu_form_txts/'
    files = glob(fpath + '*.txt')
    inp = read(files)
    outp = process(inp)
    write(outp[0], outp[1])


if __name__ == '__main__':
    main()
