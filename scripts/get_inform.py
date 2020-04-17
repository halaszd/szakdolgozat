#! /usr/bin/env python3
from glob import glob
import re
from collections import defaultdict
import argparse
import os
import sys
sys.path.append('../')
import scripts.common as c


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


def inform_past_perf(txt, vala_volt, pps):
    """
    :param inp: szöveges bemenet
        A TMK-ról letöltött 4 féle txt: tmk_perf_vala.txt, tmk_perf_volt.txt, tmk_impf_vala.txt, tmk_impf_volt.txt
    :param vala_volt: -tt + valá-t vagy -tt + volt-ot keressen a függvény
    :return: évszámok szerint növekvően rendezet gyakorisági lista [('évszám', gyakoriság), ...]

    pps: szótár a -tt + vala vagy a -tt + volt alakok számának rögzítésére évszámok szerint
        {'anydate_1':[past_perf_1, past_perf_2... past_perf_n], 'anydate_n': [...], ...}
    pat_ptype: valá-t vagy volt-ot keressen az potenciális keresett összetett múlt időkben (regex)
    pat_sqr_bracket: szögletes zárójelen belüli részt nézi
    pat_crl_bracke: kapcsos zárójelen belüli részt nézi

    Működés

    A TMK táblázatbe betölthető keresési eredményét várja inputként.
    Végigmegy a fájl tsv sorain: txtid-->date-->year-->settlement-->county-->from-->to-->soc.stat-->hit
    a létrehozott szótárban a year a kulcs, az érték egy lista, amiben az square és curly bracket-ek közötti részek
    (a sent változóban) potenciális múlt idők, lesznek a lista elemei.
    Egy sent összes zárójeles részében lévő elemet listába teszi (findall) csak akkor lehet használni egy talált
    múlt időt, ha el lehet helyezni az időben végigmegy az összes zárójelből kiszedett elemeken, amik egyenként
    potenciális múlt idők ha a zárójeles részből kiszedett stringben benne van a volt/vala, elmenti évszám szerint.
    Rendezi a szótárban lévő kúlcs-érték párokat évszámok szerint növekvő sorrendben, majd feltölti a szótár üres
    éveit egy üres listával, hogy könyebb legyen a normalizálás diagramhoz
    """

    pat_ptype = re.compile(r'[vuw]al+a\b', re.I) if vala_volt == 'vala' else re.compile(r'[vuwú][aoó]l*t+h?\b', re.I)
    pat_sqr_bracket = re.compile(r'\[\[(.+?)]')
    pat_crl_bracket = re.compile(r'{(.+?)}')
    txt = txt.split('\n')

    # TESZTELÉSHEZ
    # nomatches = []  # hibák kiszűrése, ha esetlen nem talál keresett múlt időt

    for line in txt:
        line = line.rstrip().split('\t')
        if len(line) == 9:
            year = line[2]
            sent = line[-1]
            pot_hits = pat_sqr_bracket.findall(sent) + pat_crl_bracket.findall(sent)
            if year != '':
                for pot_hit in pot_hits:
                    if pat_ptype.search(pot_hit):
                        pps[year][1].append(pot_hit)
                        pps[year][0] += 1

    # TESZTELÉSHEZ
    #                 else:  # mikor nem találta a keresett múlt időt
    #                     nomatches.append(pot_hit)
    #         else:  # mikor nincs év
    #             print(line)
    # for item in sorted(pps.items(), key=lambda item: item[0]):
    #     print(item[0] + ':', len(item[1]), item[1])
    # print('\nNOMATCHES LISTA TARTALMA\n' + '\n'.join(nomatches))

    # üres évek generálása
    # [(év, elemszám, [elemek])]


def preprocess(txt, char_map):
    for orig, norm in char_map:
        txt = txt.replace(orig, norm)
    txt = txt.replace('\xa0', '')
    return txt


def process(inp_1, inp_2, char_map, vala_volt):
    pps = defaultdict(lambda: [0, []])
    for txt in inp_1:
        txt = preprocess(txt, char_map)
        inform_past_perf(txt, vala_volt, pps)

    all_words = get_all_words(inp_2)
    for key in all_words.keys():
        if key in pps.keys():
            pps[key].append(all_words[key])
    c.gen_empty_years(sorted(all_words.keys(), key=lambda year: year), pps)

    # for item, value in pps.items():
    #     print(item, value)
    return [(elem[0], elem[1][0], elem[1][2], elem[1][1]) for elem in sorted(pps.items(), key=lambda item: item[0])]


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='Path to file', nargs='+')
    parser.add_argument('-r', '--reference', help='Path of reference file', nargs='?', default='../inputs/inform/tmk_all.txt')
    parser.add_argument('-c', '--charmap', help='Path to charmap tsv', nargs='?', default='../inputs/init/char_map.txt')
    parser.add_argument('-d', '--directory', help='Path of output file(s)', nargs='?', default='../outputs/inform')
    parser.add_argument('-f', '--ofname', help='Output filename', nargs='?', default='freq_inf_output.txt')
    parser.add_argument('-t', '--past_type',
                        help='Which text and past type it is. Separated by column, eg. INFORM.,PERF.,VALA',
                        default='# INFORM.,PERF.,VALA')

    args = parser.parse_args()
    files = []

    for p in args.filepath:
        poss_files = glob(p)
        poss_files = [os.path.abspath(x) for x in poss_files]
        files += poss_files

    return {'outdir': args.directory, 'files': files, 'ofname': args.ofname,
            'reference': args.reference, 'charmap': args.charmap, 'past_type': args.past_type}


def main():
    args = get_args()
    inp_1 = c.read_v1(args['files'])
    inp_2 = c.read_v2(args['reference'])
    char_map = c.get_char_map(c.read_v2(args['charmap']))
    past_type = c.get_past_type(args['past_type'])
    outp = process(inp_1, inp_2, char_map, past_type[1])
    c.write(outp, args['outdir'], args['ofname'], args['past_type'])


if __name__ == '__main__':
    main()
