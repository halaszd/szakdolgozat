#! /usr/bin/env python3

from glob import glob
import re
from collections import defaultdict
import argparse
import os
import sys
from string import punctuation as puncts
sys.path.append('../')
import scripts.common as c

# TODO: letölteni az Ómagyar korpusz-t, feldarabolni szóközök mentén -->
# TODO --> egyenlő a tokenizálással, mert a szavak le vannak választva a központozásról
# TODO csak a volt és csak a valát is létre kell hozni


LEXICONS = {'perf.': {'vala': '../inputs/init/form/perf_vala.txt',
                      'volt': '../inputs/init/form/perf_volt.txt'},
            'imp.': {'vala': '../inputs/init/form/imp_vala.txt',
                     'volt': '../inputs/init/form/imp_volt.txt'}}


def get_path_lexicon(t, t2):
    return LEXICONS[t][t2]


def get_lexicon(txt):
    return [line.split('\t')[0].strip() for line in txt.split('\n')]


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
            # pps[i][2] += hits
    else:
        pps[year][0] += len(hits)
        pps[year][1] += doc_length
        # pps[year][2] += hits


def form_past_perf(txt, year, vala_volt, asp, pps, is_discr, lexicon=None):
    stop_affixes = ('sag', 'seg', 'ás', 'és', 'ös' 'ős', 'ós', 'endó', 'endő', 'endo', 'andó', 'andő', 'ando',
                    'ban', 'ben', 'ba', 'be', 'lan', 'len', 'lán', 'lén', 'b', 'bb', 'tól', 'től', 'ból', 'ből',
                    'wa', 'we', 'va', 've', 'ka', 'ke',)

    # todo: ttanak ttenek impnél
    pat_vala_volt = r'([vuw]ala\b)' if vala_volt == "vala" else r'([vuwú][oó]l*t+h?)\b'

    if asp.startswith('perf'):
        pat_past = re.compile(
            r"""
            ([a-záöőüűóúéí]+?(?:t+h?
            (?:[ea]m|ele[ck]|ala[ck]|
            él|[ea]d|[áa]l|
            a|e|
            [üuöőw]n?[ck]|
            [eé]te[ck]|[aá]to[ck]|
            [eéáa][ck])?)
            \s*)""" + pat_vala_volt, re.VERBOSE | re.IGNORECASE)

    elif asp.startswith('imp') or asp.startswith('neutr'):
        pat_past = re.compile(r'([a-záöőüűóúéí]+\s*)' + pat_vala_volt, re.VERBOSE | re.IGNORECASE)

    hits = []
    for hit in pat_past.finditer(txt):
        bad_affix = False
        context = txt[hit.start() - 40:hit.start()] + txt[hit.start():hit.end() + 40]
        hit = hit.group(1).strip()
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
            hits.append(hit)

    if is_discr or not lexicon:
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


def process(inp, char_map, asp, vala_volt, is_discr, lexicon):
    pps = defaultdict(lambda: [0, []]) if is_discr or not lexicon else defaultdict(lambda: [0, 0, []])
    for txt in inp:
        txt, year = preprocess(txt, char_map)
        form_past_perf(txt, year, vala_volt, asp, pps, lexicon, is_discr)

    if is_discr or not lexicon:
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
    parser.add_argument('-d', '--directory', help='Path of output file(s)', nargs='?', default='../outputs/form')
    parser.add_argument('-f', '--ofname', help='Output filename', nargs='?', default='freq_form_output.txt')
    parser.add_argument('-l', '--def_lexicon', help='Allowing default lexicons',
                        nargs='?', type=str2bool, const=True, default=False)
    parser.add_argument('-m', '--opt_lexicon', help='Path to lexicon(s)')
    parser.add_argument('-t', '--past_type',
                        help='Which text and past type it is. Separated by column, eg. INFORM.,PERF.,VALA',
                        default='# INFORM.,PERF.,VALA')
    parser.add_argument('-x', '--not_in_lexicon', help='Using lexicon for discrimination', nargs='?',
                        type=str2bool, const=True, default=False)

    args = parser.parse_args()

    txt_type, asp, vala_volt = c.get_past_type(args.past_type)

    lexicon = None
    if args.def_lexicon:
        lexicon = get_lexicon(c.read_v2(get_path_lexicon(asp, vala_volt)))
    elif args.opt_lexicon:
        lexicon = []
        for p in glob(args.opt_lexicon):
            lexicon += get_lexicon(c.read_v2(p))

    return {'outdir': args.directory, 'files': args.filepath, 'ofname': args.ofname, 'charmap': args.charmap,
            'past_type': (txt_type, asp, vala_volt), 'not_in_lexicon': args.not_in_lexicon, 'lexicon': lexicon}


def main():
    args = get_args()
    inp = c.read_v1(args['files'])
    char_map = c.get_char_map(c.read_v2(args['charmap']))
    txt_type, asp, vala_volt = args['past_type']
    outp = process(inp, char_map, asp, vala_volt, args['lexicon'], args['not_in_lexicon'])
    c.write(outp, args['outdir'], args['ofname'], args['past_type'], args['not_in_lexicon'], args['lexicon'])


if __name__ == '__main__':
    main()