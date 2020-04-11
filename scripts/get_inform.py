import unicodedata
from glob import glob
import re
from collections import defaultdict
import argparse
import os

# TODO: a find_combchars.py-al megkeresni az összes kombinált unikód karaktert a nem normalizált szövegekben
# TODO: --> ezeket átalakítani/normalizálni (chars_to_convert-ben vannak a karakterek betűhű, név, normalizált alakjai)
# TODO: szükség van rájuk az informális szövegeknél is, mert ott sem minden normalizált

# TODO: letölteni az Ómagyar korpusz-t, feldarabolni szóközök mentén -->
# TODO --> egyenlő a tokenizálással, mert a szavak le vannak választva a központozásról

# TODO: TMK-ból külön letölteni a perf/impf + vala és külön a perf/impf + volt eredményeket (tehát 4 doksi) -->
# TODO: --> tmk keresés perf + vala/volt: C~^(VPfx\.)*V.*\.Past.* ?(([wuv]al+a)|([wuv][oó]l*t+h?))\b
# TODO: --> C~^(VPfx\.)*V.*\.Past.* ?[wuv][oó]l*t+h?\b  1268 találat - csak gyakorisági találat opció
# 1268 találatból 1194 marad, mert kiesnek azok a múlt idők, amiket nem lehet időben elhelyezni
# TODO: --> C~^(VPfx\.)*V.*\.Past.* ?[wuv]al+a\b    622 találat - csak gyakorisági találat opció
# 622 találatból 546 marad az évszámok hiányában
# TODO: --> impf
# TODO: --> C~^(?!.*\.(?:Past|Subj|Cond|Ipf|Fut|Inf))^(VPfx\.)*V.*[123][^.]*.* ?[wuv]al+a\b 309 találat
# TODO: -->  C~^(?!.*\.(?:Past|Subj|Cond|Ipf|Fut|Inf))^(VPfx\.)*V.*[123][^.]*.* ?[wuv][oó]l*t+h?\b  72 találat
# TODO: A inputs/inform/all.txt -t használni az arányok kiszámolásához informálisnál (minden szó számához viszonyítás).

# TODO: a sorted_chars_in_words.txt-t használni a karakterek normalizálásához ()
# TODO: eldönteni, hogy kell-e vala-volt argumentum.


def write(outp, odir, ofname):
    os.makedirs(odir, exist_ok=True)
    with open(os.path.join(odir, ofname), 'w', encoding='utf-8') as f:
        for item in outp:
            print('{}\t{}\t{}\t{}'.format(item[0], item[1], item[2], ','.join(item[3])), file=f)


def read_fpath(inp):
    for fl in inp:
        with open(fl, 'r', encoding='utf-8') as f:
            yield f.read()


def read_ref(inp):
    with open(inp, 'r', encoding='utf-8') as f:
        return f.read()


def get_char_map(inp):
    """

    :param inp: tsv: min két oszlop: 1 oszlop: normalizálandó karakter, 2.oszlop: amire át kell alakítani
    :return: lista tuple-ökkel, egy tuple: tup[0]=betűhű, 1=normalizált
    """
    # rendezés, a legtöbb karakterből álló betű legfelül
    lines = sorted([elem for elem in inp.split('\n')], key=lambda elem: len(elem.split('\t')[0]), reverse=True)
    return [(elem.split('\t')[0], elem.split('\t')[1]) for elem in lines if elem.strip() != '']


def gen_empty_years(years, pps):
    print(pps)
    start = int(years[0])
    end = int(years[-1])
    for i in range(start, end+1):
        if str(i) not in pps.keys():
            pps[str(i)] = [0, [], 0]
    print('\n\n', pps)


def get_all_words(inp):
    pat_annot = re.compile(r'[[\]|{}]')
    all_words = defaultdict(lambda: 0)
    for line in inp.split('\n'):
        line = line.rstrip()
        if line.strip() == '':
            continue
        line = line.split('\t')
        if len(line) == 9:
            year = line[2]
            sent = pat_annot.sub('', line[-1])
            all_words[year] += len([seq for seq in sent.split() if seq != ''])
    return all_words


def inform_past_perf(inp, vala_volt, pps):
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
    inp = inp.split('\n')

    # TESZTELÉSHEZ
    # nomatches = []  # hibák kiszűrése, ha esetlen nem talál keresett múlt időt

    for line in inp:
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


def process(inp_1, inp_2, vala_volt):
    pps = defaultdict(lambda: [0, []])
    for txt in inp_1:
        txt = txt.replace('\xa0', '')
        inform_past_perf(txt, vala_volt, pps)

    all_words = get_all_words(inp_2)
    for key in all_words.keys():
        if key in pps.keys():
            pps[key].append(all_words[key])

    gen_empty_years(sorted(pps.keys(), key=lambda year: year), pps)

    # TODO: ezután a dict-hez hozzáadni a kinyert összes szó számot / év dict[év].append(össz szószám)
    # for item, value in pps.items():
    #     print(item, value)
    return [(elem[0], elem[1][0], elem[1][2], elem[1][1]) for elem in sorted(pps.items(), key=lambda item: item[0])]


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='Path to file', nargs='+')
    parser.add_argument('-r', '--reference', help='Path of reference file')
    parser.add_argument('-d', '--directory', help='Path of output file(s)', nargs='?', default='../outputs/')
    parser.add_argument('-f', '--ofname', help='Output filename', default='freq_inf_output.txt')
    parser.add_argument('-v', '--vala_volt')

    args = parser.parse_args()
    files = []

    for p in args.filepath:
        poss_files = glob(p)
        poss_files = [os.path.abspath(x) for x in poss_files]
        files += poss_files

    return {'outdir': args.directory, 'files': files, 'ofname': args.ofname,
            'vala_volt': args.vala_volt, 'reference': args.reference}


def main():
    args = get_args()
    inp_1 = read_fpath(args['files'])
    inp_2 = read_ref(args['reference'])
    outp = process(inp_1, inp_2, args['vala_volt'])
    for out in outp:
        print(out)
    write(outp, args['outdir'], args['ofname'])


if __name__ == '__main__':
    main()
