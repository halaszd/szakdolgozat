#! /usr/bin/env python3

from glob import glob
import re
from collections import defaultdict
import argparse
import sys
from string import punctuation as puncts
sys.path.append('../')
import scripts.common as c

# A lexikonok elérési útvonala
LEXICONS = {'perf.': {'vala': '../inputs/form/lexicons/perf_vala.txt',
                      'volt': '../inputs/form/lexicons/perf_volt.txt'},
            'imp.': {'vala': '../inputs/form/lexicons/imp_vala.txt',
                     'volt': '../inputs/form/lexicons/imp_volt.txt'}}


def get_path_lexicon(t, t2):
    """

    :param t: Aspektus
    :param t2: Vala/volt
    :return: A lexikon elérési útvonala
    """
    return LEXICONS[t][t2]


def get_freq_types(hits, pps=None):
    """
    Visszaadja a találati szótárat, freqvenciával és a találati alakokkal együtt

    :param hits: A találatokat rögzítő lista tuple-öket tartalmazva
    :param pps: A szótár, amit feltölt a függvény: defaultdict(lambda: [0, []])
    :return: Találati szótár
    """
    if pps is None:
        pps = defaultdict(lambda: [0, []])
    for hit, examp in hits:
        pps[hit][0] += 1
        if len(pps[hit][1]) < 11:
            pps[hit][1].append(examp)
    return pps


def get_freq_past_by_year(hits, year, doc_length, pps=None):
    """
    Visszaadja a találati szótárat évek szerint csoportosított frekveciákkal

    :param hits: A találatokat rögzítő lista tuple-öket tartalmazva
    :param pps: A szótár, amit feltölt a függvény: {lambda: [0, 0, []]}
    :param year: A viszgált dokumentum datálása
    :param doc_length: A viszgált dokumentum hossza
    :return:
    """
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
    """
    A keresett múlt idő fajta megtalálásáért felelős függvény.

    :param txt: A bemeneti szöveg
    :param year: A dokumentum datálása
    :param vala_volt: Vala/volt típust keressen
    :param asp: A múlt idő aspektusa
    :param pps: A szótár, amit feltölt a függvény
    :param is_discr: Ha True, akkor a találatnak nem szabad benne lennie a már meglévő szótárban
    :param exp_mod: Ha True, akkor szótárat hoz létre
    :param lexicon: A bemeneti lexikon
    :return: Az eredményekkel feltöltött gyakorisági/példa szótár
    """
    # Azok a végződések, amelyek nem kapcsolódnak igékhez
    stop_affixes = ('sag', 'seg', 'ás', 'és', 'ös' 'ős', 'ós', 'endó', 'endő', 'endo', 'andó', 'andő', 'ando',
                    'ban', 'ben', 'ba', 'be', 'lan', 'len', 'lán', 'lén', 'b', 'bb', 'tól', 'től', 'ból', 'ből',
                    'wa', 'we', 'va', 've', 'ka', 'ke')

    # A regex második egységét definiálja, vala vagy volt-ra keressen rá
    pat_vala_volt = r'([vuw]ala\b)' if vala_volt == "vala" else r'([vuwú][oó]l*t+h?\b)'

    if asp.startswith('perf'):
        # Ha perfektum a múlt idő aspektusa, akkor -t(t)(személyrag) + vala/volt-ra keres rá
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
    elif asp.startswith('imp') or asp.strip() == '':
        # Ha imperfektum a múlt idő aspektusa, vagy kitöltetlen (sima volt/vala keresése esetén)
        # akkor bármilyen szó + vala/volt-ra keres rá
        pat_past = re.compile(r'([a-záöőüűóúéí]+\s*)' + pat_vala_volt, re.IGNORECASE)

    hits = []
    for hit in pat_past.finditer(txt):
        bad_affix = False
        context = txt[hit.start() - 40:hit.start()] + txt[hit.start():hit.end() + 40]
        hit = hit.group(1).strip()
        if asp.startswith('imp') or asp.startswith('perf'):
            # Csak akkor nézi a kizáró végződések litáját, ha nem sima vala/volt-ra kell keresnie
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
    """
    A szöveg feldolgozása előtti egységesítése a függvény feladata

    :param txt: Bemeneti szöveg
    :param char_map: Karakterek szótára. Soronként karakterek (TSV): mit -> mire
    :return: Egységesített szöveg
    """
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
    """

    :param inp: A dokumentum, amiből ki kell nyerni a múlt időket
    :param char_map: A karakterek szótára, soronként mit->mire alakban
    :param asp: A múlt idő aspektusa
    :param vala_volt: Volt/vala fajta összetételt keressen?
    :param is_discr: Ha True, akkor az az alak fog kelleni, ami nincs benne a lexikonban
    :param exp_mod: Lexikont létrehozása, ha True
    :param lexicon: Lexikon szavai egy listában
    """
    pps = defaultdict(lambda: [0, []]) if exp_mod else defaultdict(lambda: [0, 0, []])
    for txt in inp:
        txt, year = preprocess(txt, char_map)
        find_past(txt, year, vala_volt, asp, pps, is_discr, exp_mod, lexicon)

    if exp_mod:
        return [(elem[0], elem[1][0], elem[1][1]) for elem in sorted(pps.items(), key=lambda item: item[0])]

    # Üres évek generálása, ahol nem volt találat
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
    """
    Argumentumok összegyűjtése
    """

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
                        help="""Which text and past type it is. Three value separated by column,
                                 All values must be filled, eg. inform.,perf.,vala """,
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
            'past_type': [txt_type, asp, vala_volt], 'is_discr': args.is_discr, 'lexicon': lexicon,
            'exp_mod': args.exp_mod}


def main():
    args = get_args()
    inp = c.read_v1(args['files'])
    char_map = c.get_char_map(c.read_v2(args['charmap']))
    past_type = args['past_type']
    outp = process(inp, char_map, past_type[1], past_type[2], args['is_discr'], args['exp_mod'], args['lexicon'])
    if past_type[1].strip() == '':
        if args['is_discr']:
            past_type[1] = 'discr.'
        else:
            past_type[1] = 'non discr.'
    c.write(outp, args['outdir'], args['ofname'], past_type, args['exp_mod'])


if __name__ == '__main__':
    main()