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

# TODO: a char_map.txt-t használni a karakterek normalizálásához ()
# TODO: eldönteni, hogy kell-e vala-volt argumentum.


def write(outp):
    with open('chars_with_unicode_name.txt', 'w', encoding='utf-8') as f:
        for key, value in outp.items():
            print(key + '\t', value, file=f)


def read(inp):
    for fl in inp:
        with open(fl, 'r', encoding='utf-8') as f:
            yield f.read()


def get_char_map(inp):
    """

    :param inp: tsv: min két oszlop: 1 oszlop: normalizálandó karakter, 2.oszlop: amire át kell alakítani
    :return: lista tuple-ökkel, egy tuple: tup[0]=betűhű, 1=normalizált
    """
    # rendezés, a legtöbb karakterből álló betű legfelül
    lines = sorted([elem for elem in inp.split('\n')], key=lambda elem: len(elem.split('\t')[0]), reverse=True)
    return [(elem.split('\t')[0], elem.split('\t')[1]) for elem in lines if elem.strip() != '']


def gen_empty_years(years, pps):
    start = int(years[0])
    end = int(years[-1])
    for i in range(start, end+1):
        if str(i) not in years:
            pps[str(i)] = []


def find_form_past_perf(inp):
    # \[\[.*?\]\]|{.*?} között vannak a találatok
    # k --> c
    # == == jelet ''-re változtatni
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
    print(len(pat_past_perf.findall(inp)))
    for elem in pat_past_perf.findall((inp)):
        print(elem)


def process(inp, vala_volt):
    pps = defaultdict(lambda: [])
    for txt in inp:
        txt = txt.replace('\xa0', '')
        inform_past_perf(txt, vala_volt, pps)
        # for elem in outp:
        #     print(elem)
    gen_empty_years(sorted(pps.keys(), key=lambda key: key), pps)
    return [(elem[0], len(elem[1]), elem[1]) for elem in sorted(pps.items(), key=lambda item: item[0])]


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='Path to file', nargs='+')
    parser.add_argument('-d', '--directory', help='Path of output file(s)', nargs='?', default='../outputs/')
    parser.add_argument('-f', '--ofname', help='Output filename')
    parser.add_argument('-v', '--vala_volt')
    parser.add_argument('-s', '--inform_form')

    args = parser.parse_args()
    files = []

    for p in args.filepath:
        poss_files = glob(p)
        poss_files = [os.path.abspath(x) for x in poss_files]
        files += poss_files

    return {'outdir': args.directory, 'files': files, 'ofname': args.ofname}


def main():
    args = get_args()
    inp = read(args['files'])
    outp = process(inp, args['vala_volt'])
    write(outp)


if __name__ == '__main__':
    main()
