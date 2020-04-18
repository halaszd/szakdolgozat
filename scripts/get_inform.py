#! /usr/bin/env python3
from glob import glob
import re
from collections import defaultdict
import argparse
import sys
sys.path.append('../')
import scripts.common as c


# TODO csak a volt és csak a valát is létre kell hozni

#
# LEXICONS = {'perf.': {'vala': '../inputs/inform/lexicons/perf_vala.txt',
#                       'volt': '../inputs/inform/lexicons/perf_volt.txt'},
#             'imp.': {'vala': '../inputs/inform/lexicons/imp_vala.txt',
#                      'volt': '../inputs/inform/lexicons/imp_volt.txt'}}


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


def find_past(txt, vala_volt, pps, exp_mod, asp, lexicon):
    """
    :param txt: szöveges bemenet
        A TMK-ról letöltött 4 féle txt: tmk_perf_vala.txt, tmk_perf_volt.txt, tmk_impf_vala.txt, tmk_impf_volt.txt
    :param vala_volt: -tt + valá-t vagy -tt + volt-ot keressen a függvény
    :param pps: szótár a -tt + vala vagy a -tt + volt alakok számának rögzítésére évszámok szerint
        {'anydate_1':[past_perf_1, past_perf_2... past_perf_n], 'anydate_n': [...], ...}
    :return: évszámok szerint növekvően rendezet gyakorisági lista [('évszám', gyakoriság), ...]

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

    if vala_volt == 'vala':
        pat_past = re.compile(r'[vuw]ala\b', re.I)
    else:
        pat_past = re.compile(r'[vuwú][oó]l*t+h?\b', re.I)
    if asp.startswith('neutr'):
        pat_past = re.compile(r'[a-záöőüűóúéí]+\s*' + pat_past.pattern, re.I)

    pat_sqr_bracket = re.compile(r'\[\[(.+?)]')
    pat_crl_bracket = re.compile(r'{(.+?)}')
    pat_to_repl = re.compile(r'[[\]|{}]')
    txt = txt.split('\n')

    # TESZTELÉSHEZ
    # matches = []  # hibák kiszűrése, ha esetlen nem talál keresett múlt időt

    for line in txt:
        line = line.rstrip().split('\t')
        if len(line) == 9:
            year = line[2]
            sent = line[-1]
            if not asp.startswith('neutr'):
                pot_hits = pat_sqr_bracket.findall(sent) + pat_crl_bracket.findall(sent)
            else:
                sent = pat_to_repl.sub('', sent)
                pot_hits = pat_past.findall(sent)

            if year != '':
                for pot_hit in pot_hits:
                    if asp.startswith('neutr') or pat_past.search(pot_hit):
                        pts = [pt.strip() for pt in pot_hit.split()]
                        fpt = pts[0].lower()
                        # informálisnál ha van lexikon, akkor biztos, hogy diszkriminatívan lesz használva
                        if fpt not in lexicon:
                            # ha exp_mod, akkor a szó a kulcs és defaultdict(lambda: [0, []])
                            if exp_mod:
                                pps[fpt][0] += 1
                                pps[fpt][1].append(sent)
                            # különben az évszám a kulcs és defaultdict(lambda: [0, 0, []])
                            else:
                                pps[year][2].append(' '.join(pts).lower())
                                pps[year][0] += 1


def preprocess(txt, char_map):
    for orig, norm in char_map:
        txt = txt.replace(orig, norm)
    txt = txt.replace('\xa0', '')
    return txt


def process(inp_1, inp_2, char_map, asp, vala_volt, exp_mod, lexicon):
    pps = defaultdict(lambda: [0, []]) if exp_mod else defaultdict(lambda: [0, 0, []])
    for txt in inp_1:
        txt = preprocess(txt, char_map)
        find_past(txt, vala_volt, pps, exp_mod, asp, lexicon)

    if exp_mod:
        return [(elem[0], elem[1][0], elem[1][1]) for elem in sorted(pps.items(), key=lambda item: item[0])]

    all_words = get_all_words(inp_2)
    for key in all_words.keys():
        if key in pps.keys():
            pps[key][1] = all_words[key]
    c.gen_empty_years(sorted(all_words.keys(), key=lambda year: year), pps)

    # for item, value in pps.items():
    #     print(item, value)
    return [(elem[0], elem[1][0], elem[1][1], elem[1][2]) for elem in sorted(pps.items(), key=lambda item: item[0])]


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='Path to file', nargs='+')
    parser.add_argument('-c', '--charmap', help='Path to charmap tsv', nargs='?', default='../inputs/init/char_map.txt')
    parser.add_argument('-d', '--directory', help='Path of output file(s)', nargs='?', default='../outputs/inform')
    parser.add_argument('-e', '--exp_mod', help='Output is not freq. list but a word list with examples',
                        nargs='?', type=c.str2bool, const=True, default=False)
    parser.add_argument('-f', '--ofname', help='Output filename', nargs='?', default='freq_inf_output.txt')
    parser.add_argument('-m', '--opt_lexicon', help='Path to lexicon(s)')
    parser.add_argument('-r', '--corpus', help='Path to file to corpus text', nargs='?', default='../inputs/inform/tmk_all.txt')
    parser.add_argument('-t', '--past_type',
                        help='Which text and past type it is. Separated by column, eg. inform.,perf.,vala',
                        default='# inform.,perf.,vala')

    args = parser.parse_args()

    txt_type, asp, vala_volt = c.get_past_type(args.past_type)
    lexicon = []
    if args.opt_lexicon:
        for p in glob(args.opt_lexicon):
            lexicon += c.get_lexicon(c.read_v2(p))

    return {'outdir': args.directory, 'files': args.filepath, 'ofname': args.ofname, 'charmap': args.charmap,
            'past_type': (txt_type, asp, vala_volt), 'lexicon': lexicon, 'exp_mod': args.exp_mod, 'corpus': args.corpus}


def main():
    args = get_args()
    inp_1 = c.read_v1(args['files'])
    inp_2 = c.read_v2(args['corpus'])
    char_map = c.get_char_map(c.read_v2(args['charmap']))
    past_type = args['past_type']
    outp = process(inp_1, inp_2, char_map, past_type[1], past_type[2], args['exp_mod'],  args['lexicon'])
    c.write(outp, args['outdir'], args['ofname'], past_type, args['exp_mod'])


if __name__ == '__main__':
    main()
