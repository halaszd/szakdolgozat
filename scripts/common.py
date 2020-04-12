#! /usr/bin/env python3
import os


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


if __name__ == '__main__':
    pass
