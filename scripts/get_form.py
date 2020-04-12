from glob import glob
import re
from collections import defaultdict
import argparse
import os

# TODO: letölteni az Ómagyar korpusz-t, feldarabolni szóközök mentén -->
# TODO --> egyenlő a tokenizálással, mert a szavak le vannak választva a központozásról
# TODO csak a volt és csak a valát is létre kell hozni


def write(outp, odir, ofname, past_type):
    os.makedirs(odir, exist_ok=True)
    with open(os.path.join(odir, ofname), 'w', encoding='utf-8') as f:
        print('# {}'.format(past_type), file=f)
        for item in outp:
            print('{}\t{}\t{}\t{}'.format(item[0], item[1], item[2], ','.join(item[3])), file=f)


def read_v1(inp):
    for fl in inp:
        with open(fl, 'r', encoding='utf-8') as f:
            yield f.read()


def read_v2(inp):
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
    """
    :param years: lista évekkel sorrendben
    :param pps: egy múlt fajta és annak gyakorisági szótára

    Az üres éveket teszi bele a szótárba, hogy könyebb legyen belőle létrehozni később egy diagramot a matpotlibbel.
    Amelyik év nem szerepel a szótárban azt létrehozza: kulcs = év, value = 0 gyakoriság üres szótárral,
    a végén pedig 1, mint összes szó száma. Azért kell ide 1-es, hogy ne fordulhasson elő 0-val való osztás a
    gyakoriságok arányainak kiszámolásakor.
    """
    start = int(years[0])
    end = int(years[-1])
    for i in range(start, end+1):
        if str(i) not in pps.keys():
            pps[str(i)] = [0, [], 1]


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





def process(inp_1, inp_2, chars, vala_volt):
    pps = defaultdict(lambda: [0, []])
    for txt in inp_1:
        for char in get_char_map(chars):
            txt = txt.replace(char[0], char[1])
        txt = txt.replace('\xa0', '')
        inform_past_perf(txt, vala_volt, pps)

    all_words = get_all_words(inp_2)
    for key in all_words.keys():
        if key in pps.keys():
            pps[key].append(all_words[key])
    gen_empty_years(sorted(all_words.keys(), key=lambda year: year), pps)

    # TODO: ezután a dict-hez hozzáadni a kinyert összes szó számot / év dict[év].append(össz szószám)
    # for item, value in pps.items():
    #     print(item, value)
    return [(elem[0], elem[1][0], elem[1][2], elem[1][1]) for elem in sorted(pps.items(), key=lambda item: item[0])]


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='Path to file', nargs='+')
    parser.add_argument('-r', '--reference', help='Path of reference file', default='../inputs/inform/tmk_all.txt')
    parser.add_argument('-c', '--charmap', help='Path to charmap tsv', default='../inputs/init/char_map.txt')
    parser.add_argument('-d', '--directory', help='Path of output file(s)', nargs='?', default='../outputs/inform')
    parser.add_argument('-f', '--ofname', help='Output filename', default='freq_inf_output.txt')
    parser.add_argument('-t', '--past_type', help='Metadata for output:which text and past type it is',
                        default='# FORM/INFORM,PAST')
    parser.add_argument('-v', '--vala_volt')

    args = parser.parse_args()
    files = []

    for p in args.filepath:
        poss_files = glob(p)
        poss_files = [os.path.abspath(x) for x in poss_files]
        files += poss_files

    return {'outdir': args.directory, 'files': files, 'ofname': args.ofname, 'vala_volt': args.vala_volt,
            'reference': args.reference, 'charmap': args.charmap, 'past_type': args.past_type}


def main():
    args = get_args()
    inp_1 = read_v1(args['files'])
    inp_2 = read_v2(args['reference'])
    chars = read_v2(args['charmap'])
    outp = process(inp_1, inp_2, chars, args['vala_volt'])
    write(outp, args['outdir'], args['ofname'], args['past_type'])


if __name__ == '__main__':
    main()

