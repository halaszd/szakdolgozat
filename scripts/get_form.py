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


pth_lexicon = '../inputs/init'


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


def form_past_perf(txt, year, vala_volt, perf_imp, pps, lexicon=None, first_step=True):
    # TODO: a first step-pet lehet ki lehet váltani not lexikonnal
    # TODO: a ban-ben-ba-be-ket ki lehet venni mindenhonnan
    # TODO: --> s[ae]+g\b
    # TODO: --> [áéőöó]+s
    # TODO: --> [ea]nd[óőo]
    # TODO --> l[aeáé]+n  | \w+?b+\b  | a hoz-höz veszélyes
    # todo: tól-től | ból-ből
    # todo: wva-wve ka-ke
    # todo: gas-ges
    # todo: ttanak ttenek impnél
    # TODO: argok közé felvenni az imp_perf_et is, és aszerint összeállítani a regex első felét
    # TODO befejezetlennél: a kersési eredméyn - tt + vala/volt szűrt lista
    pat_vala_volt = r'([vuw]ala\b)' if vala_volt == "vala" else r'([vuwú][aoó]l*t+h?)\b'

    if perf_imp == 'perf':
        pat_past = re.compile(
            r"""
            ([a-záöőüűóúéí]+?(?:t+h?
            (?:[ea]m|elek|alak|
            él|[ea]d|[áa]l|
            a|e|
            [üuöő]n?k|
            [eé]tek|[aá]tok|
            [eéáa]k)?)
            \s*)""" + pat_vala_volt, re.VERBOSE | re.IGNORECASE)
    else:
        pat_past = re.compile(r'([a-záöőüűóúéí]+\s*)' + pat_vala_volt, re.VERBOSE | re.IGNORECASE)
    pat_past = re.compile(r'([a-záöőüűóúéí]+)\s*' + pat_vala_volt, re.IGNORECASE)

    hits = []
    for hit in pat_past.finditer(txt):
        context = txt[hit.start() - 40:hit.start()] + txt[hit.start():hit.end() + 40]
        hit = hit.group(1).strip()
        if not lexicon:
            hits.append((hit, context))
        elif first_step:
            if hit not in lexicon:
                hits.append((hit, context))
        elif hit in lexicon:
            print(hit)
            hits.append(hit)

    if first_step or not lexicon:
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


def process(inp, char_map, perf_imp, vala_volt, lexicon, first_step):
    pps = defaultdict(lambda: [0, []]) if first_step or not lexicon else defaultdict(lambda: [0, 0, []])
    for txt in inp:
        txt, year = preprocess(txt, char_map)
        form_past_perf(txt, year, vala_volt, perf_imp, pps, lexicon, first_step)

    if first_step or not lexicon:
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
    parser.add_argument('-t', '--past_type', help='Metadata for output:which text and past type it is',
                        default='# INFORM,PERF. + VALA')
    parser.add_argument('-i', '--perf_imp', help='Selects the aspect of the past to find', default='perf')
    parser.add_argument('-l', '--lexicon', help='Path to lexicon of to be searched pat')
    parser.add_argument('-v', '--vala_volt', help='Vala or volt type past to search', nargs='?', default='vala')
    parser.add_argument('-x', '--first_step', help='First step: collect the set of declared past', nargs='?',
                        type=str2bool, const=True, default=False)

    # '../inputs/init/form/init_perf_vala.txt  < lexikon helye

    args = parser.parse_args()
    files = []

    for p in args.filepath:
        poss_files = glob(p)
        poss_files = [os.path.abspath(x) for x in poss_files]
        files += poss_files

    return {'outdir': args.directory, 'files': files, 'ofname': args.ofname, 'vala_volt': args.vala_volt,
            'charmap': args.charmap, 'past_type': args.past_type, 'first_step': args.first_step,
            'perf_imp': args.perf_imp, 'lexicon': args.lexicon}


def main():
    args = get_args()
    inp = c.read_v1(args['files'])
    char_map = c.get_char_map(c.read_v2(args['charmap']))
    lexicon = args['lexicon']
    if lexicon:
        lexicon = get_lexicon(c.read_v2(args['lexicon']))

    outp = process(inp, char_map, args['perf_imp'], args['vala_volt'], lexicon, args['first_step'])
    c.write(outp, args['outdir'], args['ofname'], args['past_type'], args['first_step'], lexicon)


if __name__ == '__main__':
    main()