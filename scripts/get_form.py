#! /usr/bin/env python3

from glob import glob
import re
from collections import defaultdict
import argparse
import os
import sys
sys.path.append('../')
import scripts.common as c

# TODO: letölteni az Ómagyar korpusz-t, feldarabolni szóközök mentén -->
# TODO --> egyenlő a tokenizálással, mert a szavak le vannak választva a központozásról
# TODO csak a volt és csak a valát is létre kell hozni


def get_all_words(inp):
    pat_annot = re.compile(r'[[\]|{}]')
    all_words = defaultdict(lambda: 0)
    for line in inp.split('\n')[1:]:
        line = line.rstrip()
        if line.strip() == '':
            continue
        line = line.split('\t')
        if len(line) == 9:
            year = line[2]
            if not year.isdigit():
                continue
            sent = pat_annot.sub('', line[-1])
            all_words[year] += len([seq for seq in sent.split() if seq != ''])
    return all_words


def form_past_perf(inp, vala_volt, pps):
    pat_past_perf = re.compile(
        r"""
        ([a-záöőüűóúéí]+?(?:t+h?
        (?:[ea]m|elek|alak|
        él|[ea]d|[áa]l|
        a|e|
        [üu]n?k|
        [eé]tek|[aá]tok|
        [eéáa]k)?)
        \s*
        (?:([vuw]al+a\b)|
        ([vuwú][aoó]l*t+h?\b)))
        """, re.VERBOSE | re.IGNORECASE)

    # print(len(pat_past_perf.findall(inp)))
    for elem in pat_past_perf.findall((inp)):
        pps[elem[0]][0] += 1


def preprocess(txt, chars):
    # TODO: replace: r'\n-+' --> "", '-@@' --> '', '@@-' --> '', '== ==' -> ' '
    pat_splitted = re.compile(r'-\n-|-\n|\n', re.MULTILINE)
    for char in c.get_char_map(chars):
        txt = txt.replace(char[0], char[1])
    txt = pat_splitted.sub('', txt).replace('-@@', '').replace('@@-', '').replace('== ==', '')
    # print(txt)
    return txt


def process(inp, chars, vala_volt):
    # pps = defaultdict(lambda: [0, []])
    pps = defaultdict(lambda: [0])
    for txt in inp:
        txt = preprocess(txt, chars)
        form_past_perf(txt, vala_volt, pps)

    # teszthez
    for elem in sorted(pps.items(), key=lambda item: item[1][0], reverse=True):
        print(elem, end="  ### ")

    # all_words = get_all_words(inp)
    # for key in all_words.keys():
    #     if key in pps.keys():
    #         pps[key].append(all_words[key])
    #     c.gen_empty_years(sorted(all_words.keys(), key=lambda year: year), pps)
    # return [(elem[0], elem[1][0], elem[1][2], elem[1][1]) for elem in sorted(pps.items(), key=lambda item: item[0])]


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='Path to file', nargs='+')
    parser.add_argument('-c', '--charmap', help='Path to charmap tsv', default='../inputs/init/char_map.txt')
    parser.add_argument('-d', '--directory', help='Path of output file(s)', nargs='?', default='../outputs/inform')
    parser.add_argument('-f', '--ofname', help='Output filename', default='freq_inf_output.txt')
    parser.add_argument('-t', '--past_type', help='Metadata for output:which text and past type it is',
                        default='# FORM/INFORM,PAST')
    parser.add_argument('-v', '--vala_volt', help='Vala or volt type past to search', default='vala')

    args = parser.parse_args()
    files = []

    for p in args.filepath:
        poss_files = glob(p)
        poss_files = [os.path.abspath(x) for x in poss_files]
        files += poss_files

    return {'outdir': args.directory, 'files': files, 'ofname': args.ofname,
            'vala_volt': args.vala_volt, 'charmap': args.charmap, 'past_type': args.past_type}


def main():
    args = get_args()
    inp = c.read_v1(args['files'])
    chars = c.read_v2(args['charmap'])
    outp = process(inp, chars, args['vala_volt'])
    # c.write(outp, args['outdir'], args['ofname'], args['past_type'])


if __name__ == '__main__':
    main()

