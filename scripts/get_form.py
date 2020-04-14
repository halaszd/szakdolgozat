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
    pat_annot = re.compile(r'[[\]|{}/]')
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


def get_freq_types(hits, pps=None):
    if pps is None:
        pps = defaultdict(lambda: [0, []])
    for hit, examp in hits:
        pps[hit][0] += 1
        if len(pps[hit][1]) < 11:
            pps[hit][1].append(examp)
    return pps


def get_freq_past(seq_ls, year, pps=None):
    if pps is None:
        pps = defaultdict(lambda: [0, []])


def form_past_perf(txt, vala_volt, pps, first_step, year):
    # TODO: argok közé felvenni az imp_perf_et is, és aszerint összeállítani a regex első felét
    # TODO befejezetlennél: a kersési eredméyn - tt + vala/volt szűrt lista
    vala_volt = r'[vuw]al+a\b' if vala_volt == "vala" else r'[vuwú][aoó]l*t+h?\b'
    pat_past_perf = re.compile(
        r"""
        [a-záöőüűóúéí]+?(?:t+h?
        (?:[ea]m|elek|alak|
        él|[ea]d|[áa]l|
        a|e|
        [üu]n?k|
        [eé]tek|[aá]tok|
        [eéáa]k)?)
        \s*""" + vala_volt, re.VERBOSE | re.IGNORECASE)

    hits = []
    for hit in pat_past_perf.finditer(txt):
        hits.append((hit.group(), txt[hit.start()-40:hit.start()] + txt[hit.start():hit.end() + 40]))

    if first_step:
        get_freq_types(hits, pps)
    else:
        get_freq_past(hits, year, pps)


def preprocess(txt, chars):
    pat_bracket = re.compile(r'({.*?})|(\[.*?])|/', re.MULTILINE)
    repls = [('-@@', ''), ('@@-', ''), ('== ==', ''), ('-\n-', ''), ('-\n', ''),  ('\n-', ''), ('\n', '')]
    year = source = None

    for line in txt.split('\n'):
        if line.startswith('#'):
            meta_type = line.split('# ')[1]
            meta = line.split('=')[1]
            if meta_type.startswith('year'):
                year = meta
            elif meta_type.startswith('source'):
                source = meta
        if year and source:
            break

    if source == 'orig':
        for char in c.get_char_map(chars):
            txt = txt.replace(char[0], char[1])
    txt = pat_bracket.sub('', txt)
    for seq, repl in repls:
        txt = txt.replace(seq, repl)

    return txt.lower(), year


def process(inp, chars, vala_volt, first_step):
    pps = defaultdict(lambda: [0, []])
    if first_step:
        for txt in inp:
            txt, year = preprocess(txt, chars)
            form_past_perf(txt, vala_volt, pps, first_step, year)
        return [(elem[0], elem[1][0], elem[1][1]) for elem in sorted(pps.items(), key=lambda item: item[0])]

    # else
    for txt in inp:
        txt, year = preprocess(txt, chars)
        form_past_perf(txt, vala_volt, pps, first_step, year)

    # teszthez

    # all_words = get_all_words(inp)
    # for key in all_words.keys():
    #     if key in pps.keys():
    #         pps[key].append(all_words[key])
    #     c.gen_empty_years(sorted(all_words.keys(), key=lambda year: year), pps)
    # return [(elem[0], elem[1][0], elem[1][2], elem[1][1]) for elem in sorted(pps.items(), key=lambda item: item[0])]


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='Path to file', nargs='+')
    parser.add_argument('-c', '--charmap', help='Path to charmap tsv', nargs='?', default='../inputs/init/char_map.txt')
    parser.add_argument('-d', '--directory', help='Path of output file(s)', nargs='?', default='../outputs/inform')
    parser.add_argument('-f', '--ofname', help='Output filename', nargs='?', default='freq_inf_output.txt')
    parser.add_argument('-t', '--past_type', help='Metadata for output:which text and past type it is',
                        default='# INFORM,PERF. + VALA')
    parser.add_argument('-v', '--vala_volt', help='Vala or volt type past to search', nargs='?', default='vala')
    parser.add_argument('-x', '--first_step', help='First step: collect the set of declared past', nargs='?',
                        type=str2bool, const=True, default=False)

    args = parser.parse_args()
    files = []

    for p in args.filepath:
        poss_files = glob(p)
        poss_files = [os.path.abspath(x) for x in poss_files]
        files += poss_files

    return {'outdir': args.directory, 'files': files, 'ofname': args.ofname, 'vala_volt': args.vala_volt,
            'charmap': args.charmap, 'past_type': args.past_type, 'first_step': args.first_step}


def main():
    args = get_args()
    inp = c.read_v1(args['files'])
    chars = c.read_v2(args['charmap'])
    outp = process(inp, chars, args['vala_volt'], args['first_step'])
    c.write(outp, args['outdir'], args['ofname'], args['past_type'], True)


if __name__ == '__main__':
    main()