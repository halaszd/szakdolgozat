#! /usr/bin/env python3

from glob import glob
import re
from collections import defaultdict
import argparse
import sys
from string import punctuation as puncts
sys.path.append('../')
import scripts.common as c


LEXICONS = {'perf.': {'vala': '../inputs/form/lexicons/perf_vala.txt',
                      'volt': '../inputs/form/lexicons/perf_volt.txt'},
            'imp.': {'vala': '../inputs/form/lexicons/imp_vala.txt',
                     'volt': '../inputs/form/lexicons/imp_volt.txt'}}


def get_path_lexicon(t, t2):
    return LEXICONS[t][t2]


def get_freq_types(hits, pps=None):
    if pps is None:
        pps = defaultdict(lambda: [0, []])
    for hit, examp in hits:
        pps[hit][0] += 1
        if len(pps[hit][1]) < 11:
            pps[hit][1].append(examp)
    return pps


def get_freq_past_by_year(hits, year, doc_length, pps=None):
    if pps is None:
        pps = {lambda: [0, 0, []]}

    years = year.split('-')
    if len(years) == 2:
        interval = int(years[1]) - int(years[0]) + 1
        for i in range(int(years[0]), int(years[1])+1):
            pps[str(i)][0] += len(hits) / interval
            pps[str(i)][1] += doc_length / interval
    else:
        pps[year][0] += len(hits)
        pps[year][1] += doc_length


def find_past(txt, year, vala_volt, asp, pps, is_discr, exp_mod, lexicon):
    stop_affixes = ('sag', 'seg', 'ás', 'és', 'ös' 'ős', 'ós', 'endó', 'endő', 'endo', 'andó', 'andő', 'ando',
                    'ban', 'ben', 'ba', 'be', 'lan', 'len', 'lán', 'lén', 'b', 'bb', 'tól', 'től', 'ból', 'ből',
                    'wa', 'we', 'va', 've', 'ka', 'ke')

    pat_vala_volt = r'([vuw]ala\b)' if vala_volt == "vala" else r'([vuwú][oó]l*t+h?\b)'

    if asp.startswith('perf'):
        pat_past = re.compile(
            r"""
            ([a-záöőüűóúéí]+?(?:t+h?    # Bármi egészen a t + esetleges személyragokig
            (?:[ea]m|ele[ck]|ala[ck]|   # E/1
            él|[ea]d|[áa]l|             # E/2
            a|e|                        # E/3
            [üuöőw]n?[ck]|              # T/1
            [eé]te[ck]|[aá]to[ck]|      # T/2
            [eéáa][ck])?)               # T/3, az eddig tartó rész egy elmenthető egység
            \s*)"""                     # Utána nullával egyenlő vagy több whitespace
            + pat_vala_volt,            # a vala vagy volt mintázat inputtól függően
            re.VERBOSE | re.IGNORECASE)

    elif asp.startswith('imp') or asp.startswith('discr'):
        pat_past = re.compile(r'([a-záöőüűóúéí]+\s*)' + pat_vala_volt, re.IGNORECASE)

    hits = []
    for hit in pat_past.finditer(txt):
        bad_affix = False
        context = txt[hit.start() - 40:hit.start()] + txt[hit.start():hit.end() + 40]
        hit = hit.group(1).strip()
        if not is_discr:
            for affix in stop_affixes:
                if hit.endswith(affix):
                    bad_affix = True
                    break
        if bad_affix:
            continue
        if not lexicon:
            hits.append((hit, context))
        elif is_discr:
            if hit not in lexicon:
                hits.append((hit, context))
        elif hit in lexicon:
            hits.append((hit, context))

    if exp_mod:
        get_freq_types(hits, pps)
    else:
        get_freq_past_by_year(hits, year, len([item for item in txt.split() if item not in puncts]), pps)


def preprocess(txt, char_map):
    pat_bracket = re.compile(r'({.*?})|(\[.*?])|/', re.MULTILINE)
    repls = [('-@@', ''), ('@@-', ''), ('== ==', ' '), ('-\n-', ''), ('-\n', ''),  ('\n-', ''), ('\n', ''), ('\'', '')]
    year = source = None
    i = 0
    txt = txt.split('\n')
    while not (year and source) and i < len(txt)-1:
        if txt[i].startswith('#'):
            line = txt.pop(i)
            meta_type = line.split('# ')[1]
            meta = line.split('=')[1]
            if meta_type.startswith('year'):
                year = meta
            elif meta_type.startswith('source'):
                source = meta
        else:
            i += 1

    txt = '\n'.join(txt)
    if source == 'orig':
        for orig, norm in char_map:
            txt = txt.replace(orig, norm)
    txt = pat_bracket.sub('', txt)
    for seq, repl in repls:
        txt = txt.replace(seq, repl)

    return txt.lower(), year


def process(inp, char_map, asp, vala_volt, is_discr, exp_mod, lexicon):
    pps = defaultdict(lambda: [0, []]) if exp_mod else defaultdict(lambda: [0, 0, []])
    for txt in inp:
        txt, year = preprocess(txt, char_map)
        find_past(txt, year, vala_volt, asp, pps, is_discr, exp_mod, lexicon)

    if exp_mod:
        return [(elem[0], elem[1][0], elem[1][1]) for elem in sorted(pps.items(), key=lambda item: item[0])]

    c.gen_empty_years(sorted(pps.keys(), key=lambda y: y), pps)

    return [(elem[0], '{:.2f}'.format(elem[1][0]), '{:.2f}'.format(elem[1][1]), elem[1][2])
            for elem in sorted(pps.items(), key=lambda item: item[0])]

    # teszthez

    # for key in all_words.keys():
    #     if key in pps.keys():
    #         pps[key].append(all_words[key])
    #     c.gen_empty_years(sorted(all_words.keys(), key=lambda year: year), pps)
    # return [(elem[0], elem[1][0], elem[1][2], elem[1][1]) for elem in sorted(pps.items(), key=lambda item: item[0])]


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='Path to file', nargs='+')
    parser.add_argument('-c', '--charmap', help='Path to charmap tsv', nargs='?', default='../inputs/init/char_map.txt')
    parser.add_argument('-d', '--directory', help='Path of output file(s)', nargs='?', default='../outputs/form')
    parser.add_argument('-e', '--exp_mod', help='Output is not freq. list but a word list with examples',
                        nargs='?', type=c.str2bool, const=True, default=False)
    parser.add_argument('-f', '--ofname', help='Output filename', nargs='?', default='freq_form_output.txt')
    parser.add_argument('-l', '--def_lexicon', help='Allowing default lexicons',
                        nargs='?', type=c.str2bool, const=True, default=False)
    parser.add_argument('-m', '--opt_lexicon', help='Path to lexicon(s)')
    parser.add_argument('-t', '--past_type',
                        help='Which text and past type it is. Separated by column, eg. INFORM.,PERF.,VALA',
                        default='# inform.,perf.,vala')
    parser.add_argument('-x', '--is_discr', help='Using lexicon for discrimination', nargs='?',
                        type=c.str2bool, const=True, default=False)

    args = parser.parse_args()

    txt_type, asp, vala_volt = c.get_past_type(args.past_type)
    lexicon = None
    if args.def_lexicon:
        lexicon = c.get_lexicon(c.read_v2(get_path_lexicon(asp, vala_volt)))
    elif args.opt_lexicon:
        lexicon = []
        for p in glob(args.opt_lexicon):
            lexicon += c.get_lexicon(c.read_v2(p))
    if not lexicon:
        args.is_discr = False

    return {'outdir': args.directory, 'files': args.filepath, 'ofname': args.ofname, 'charmap': args.charmap,
            'past_type': (txt_type, asp, vala_volt), 'is_discr': args.is_discr, 'lexicon': lexicon,
            'exp_mod': args.exp_mod}


def main():
    args = get_args()
    inp = c.read_v1(args['files'])
    char_map = c.get_char_map(c.read_v2(args['charmap']))
    txt_type, asp, vala_volt = args['past_type']
    outp = process(inp, char_map, asp, vala_volt, args['is_discr'], args['exp_mod'], args['lexicon'])
    c.write(outp, args['outdir'], args['ofname'], args['past_type'], args['exp_mod'])


if __name__ == '__main__':
    main()