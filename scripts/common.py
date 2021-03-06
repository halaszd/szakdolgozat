#! /usr/bin/env python3
import os
import argparse


def write(outp, odir, ofname, past_type, exp_mod):
    os.makedirs(odir, exist_ok=True)
    with open(os.path.join(odir, ofname), 'w', encoding='utf-8') as f:
        print('# {},{},{}'.format(past_type[0], past_type[1], past_type[2]), file=f)
        for item in outp:
            if exp_mod:
                print('{}\t{}\t{}'.format(item[0], item[1], " || ".join(item[2])), file=f)
            else:
                print('{}\t{}\t{}\t{}'.format(item[0], item[1], item[2], ','.join(item[3])), file=f)


def read_v1(inp):
    for fl in inp:
        with open(fl, 'r', encoding='utf-8') as f:
            yield f.read()


def read_v2(inp):
    with open(inp, 'r', encoding='utf-8') as f:
        return f.read()


def get_lexicon(txt):
    """

    :param txt: Bemeneti lexikon, a sorok (TSV) nulladik helyén a szóval
    :return: A lexikon szavai egy listában
    """
    return [line.split('\t')[0].strip() for line in txt.split('\n')]


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
            pps[str(i)] = [0, 1, []]


def str2bool(v):
    """
    Eldönti, hogy az argumentum Igaz, vagy Hamis értéket képvisel

    :param v: argumentum értéke
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_past_type(desc):
    """

    :param desc: a múlt idő leírása vesszőkkel elválasztva
    :return: a múlt idő meghatározása tuple-ben: 0=inform,form; 1=aspektus; 2=vala/volt
    """
    desc = desc.lower().split(',')
    return desc[0], desc[1], desc[2]


if __name__ == '__main__':
    pass
