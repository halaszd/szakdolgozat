#! /usr/bin/env python3
import matplotlib.pyplot as plt
import argparse
import sys
sys.path.append('../')
from scripts.common import str2bool

# Irányvonalak színének és alakjának beállításai a múlt idő fajtája szerint

"""
('solid', 'solid'),      # Same as (0, ()) or '-'
('dotted', 'dotted'),    # Same as (0, (1, 1)) or ':'
('dashed', 'dashed'),    # Same as '--'
('dashdot', 'dashdot')]  # Same as '-.'
"""

# TODO: argumentumként lehessen megadni, hogy a LINES a LINES_DIAKR VAGY A LINES_SZAKD szótárral legyen egyenlő,
#  tehát, hogy milyen vonaltípusokat hozzon létre a program.

LINES_DIAKR = {'inform.':
             {'perf.':
                  {'vala': ('black', '-'),
                   'volt': ('black', '--')},
              'imp.':
                  {'vala': ('black', ':'),
                   'volt': ('black', '-.')},
              'discr.':
                  {'vala': ('black', '-'),
                   'volt': ('black', '--')},
              'non discr.':
                  {'vala': ('black', '-'),
                   'volt': ('black', '--')}},
         'form.':
             {'perf.':
                  {'vala': ('gray', '-'),
                   'volt': ('gray', '--')},
              'imp.':
                  {'vala': ('gray', ':'),
                   'volt': ('gray', '-.')},
              'discr.':
                  {'vala': ('gray', '-'),
                   'volt': ('gray', '--')},
              'non discr.':
                  {'vala': ('gray', '-'),
                   'volt': ('gray', '--')}
              }}

LINES_SZAKD = {'inform.':
             {'perf.':
                  {'vala': ('red', '-'),
                   'volt': ('blue', '-')},
              'imp.':
                  {'vala': ('green', '-'),
                   'volt': ('brown', '-')},
              'discr.':
                  {'vala': ('red', '-'),
                   'volt': ('blue', '-')},
              'non discr.':
                  {'vala': ('red', '-'),
                   'volt': ('blue', '-')}},
         'form.':
             {'perf.':
                  {'vala': ('red', '--'),
                   'volt': ('blue', '--')},
              'imp.':
                  {'vala': ('green', '--'),
                   'volt': ('brown', '--')},
              'discr.':
                  {'vala': ('red', '--'),
                   'volt': ('blue', '--')},
              'non discr.':
                  {'vala': ('red', '--'),
                   'volt': ('blue', '--')}
              }}

LINES = LINES_SZAKD


def read(inp):
    for fl in inp:
        with open(fl, 'r', encoding='utf-8') as f:
            print(fl)
            yield f.read()


def split_years(freq_ls, c):
    """
    A beállított éves bontás szerint rendezi újra az adatokat

    :param freq_ls: Frekvencia lista
    :param c: Bontás mértéke
    :return: Egy meghatározott bontás által újra felépített tuple lista
    """
    count = 0
    sum_pfreq = 0
    sum_all_freq = 0
    new_freq_ls = []
    first = True
    for i, (year, pfreq, all_freq) in enumerate(freq_ls):
        sum_pfreq += float(pfreq)
        sum_all_freq += float(all_freq)
        count += 1
        if count == c:
            if first:
                new_freq_ls.append(('{}-{}'.format(freq_ls[0][0], year), sum_pfreq, sum_all_freq))
                first = False
            else:
                new_freq_ls.append((year, sum_pfreq, sum_all_freq))
            sum_pfreq = 0
            sum_all_freq = 0
            count = 0
        if i == len(freq_ls)-1 and count > 0:
            new_freq_ls.append((year, sum_pfreq, sum_all_freq))
    return new_freq_ls


def unify_years(all_ls, start, end):
    """
    Az eltérő időintervallummal rendelkező frekvencia listák egységesítése a feladata.
    Csak akkor hívódik meg, ha előre jelezzük -m argumentummal, hogy eltérő a dokumentumok kezdeti és utolsó éve

    :param all_ls: Az összes fajta múlt idő listája
    :param start: Az összes dokumentum kezdő éve közüli maximum érték
    :param end: Az összes dokumentum utolsó éve közüli minimum érték
    :return: A kezdő és utolsó év közötti frekvenciák dokumentumonként
    """
    new_all_ls = []
    for ls in all_ls:
        new_ls = [ls.pop(0)]
        i = 0
        j = len(ls) - 1
        if int(ls[0][0]) < start:
            i += 1
            while int(ls[i][0]) < start:
                i += 1
        if int(ls[j][0]) > end:
            j -= 1
            while int(ls[j][0]) > end:
                j -= 1
        new_all_ls.append(new_ls + ls[i:j+1])
    return new_all_ls


def get_start_end(all_ls):
    """
    Meghatározza az összes bemeneti dokumentum egységesített kezdeti és utolsó évét.
    Csak akkor hívódik meg, ha előre jelezzük -m argumentummal, hogy eltérő a dokumentumok kezdeti és utolsó éve

    :param all_ls: Az összes fajta múlt idő listája
    max_start: Az összes kezdeti év maximuma lesz a végső értéke
    min_end: Az összes utolsó év minimuma lesz a végső értéke
    :return: max_start, min_end
    """
    max_start = int(all_ls[0][1][0])
    min_end = int(all_ls[0][-1][0])
    for ls in all_ls[1:]:
        start = int(ls[1][0])
        end = int(ls[-1][0])
        if max_start < start:
            max_start = start
        if min_end > end:
            min_end = end
    return max_start, min_end


def get_plot(freq_ls, past_type, line_name):
    """
    A diagramhoz hozzáad egy frekvencia listából létrehozott irányvonalat

    :param freq_ls: az egyik múlt idő fajtához tartozó frekvencia lista
    :param past_type: A múlt idő fajtája, ez alapján lesz meghatározva a diagram vonalának színe, alakja
    :param line_name: A vonal neve
    """
    years = [item[0] for item in freq_ls]
    freq = [(float(item[1])/float(item[2]))*100 for item in freq_ls]
    line_type = LINES[past_type[0]][past_type[1]][past_type[2]]
    plt.plot(years, freq, label=line_name.upper(), color=line_type[0], linestyle=line_type[1])


def process(inp, interval, is_mixed):
    """
    Feladata a bemenet(ek) alapján létrehozni egy diagramot

    :param inp: Generátor, a frekvencia listákkal (szövegesen)
    :param interval: Milyen éves bontásban reprezentálja a statisztikákat
    :param is_mixed: Eltérőek-e a dokumentumok kezdeti és utolsó évei?
    """
    all_freq_ls = []
    for i, fl in enumerate(inp):
        fl = fl.split('\n')
        past_type = fl.pop(0).replace('# ', '').split(',')
        freq_ls = [past_type]
        for line in fl:
            line = line.strip()
            if line == '':
                continue
            line = line.split('\t')
            freq_ls.append((line[0], line[1], line[2]))
        all_freq_ls.append(freq_ls)

    if is_mixed:
        max_start, min_end = get_start_end(all_freq_ls)
        all_freq_ls = unify_years(all_freq_ls, max_start, min_end)
    for freq_ls in all_freq_ls:
        past_type = freq_ls.pop(0)
        freq_ls = split_years(freq_ls, interval)
        join_with = '{} {} + {}' if 'discr' not in past_type[1].lower() else '{} {} {}'
        get_plot(freq_ls, past_type, join_with.format(past_type[0], past_type[1], past_type[2]))
    plt.legend()
    plt.show()


def get_args():
    """
    Argumentumok összegyűjtése
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='Path to file', nargs='+')
    parser.add_argument('-i', '--interval', help='Split timeline rate', nargs='?', default=50, type=int)
    parser.add_argument('-m', '--is_mixed', help='If to create plot from inform. and form. text type', nargs='?',
                        type=str2bool, const=True, default=False)

    args = parser.parse_args()

    return {'files': args.filepath, 'interval': args.interval, 'is_mixed': args.is_mixed}


def main():
    args = get_args()

    inp = read(args['files'])
    process(inp, args['interval'], args['is_mixed'])


if __name__ == '__main__':
    main()
