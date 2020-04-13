#! /usr/bin/env python3
import matplotlib.pyplot as plt
from glob import glob
import argparse
import os


LINES = {'INFORM':
             {'PERF. + VALA': ('red', '-'),
              'PERF. + VOLT': ('yellow', '-'),
              'IMP. + VALA': ('green', '-'),
              'IMP. + VOLT': ('brown', '-')},
         'FORM':
             {'PERF. + VALA': ('red', '--'),
              'PERF. + VOLT': ('yellow', '--'),
              'IMP. + VALA': ('green', '--'),
              'IMP. + VOLT': ('brown', '--')}}


def read(inp):
    for fl in inp:
        with open(fl, 'r', encoding='utf-8') as f:
            yield f.read()


def split_years(freq_ls, c=1):
    count = 0
    sum_pfreq = 0
    sum_all_freq = 0
    new_freq_ls = []
    first = True
    for i, (year, pfreq, all_freq) in enumerate(freq_ls):
        sum_pfreq += int(pfreq)
        sum_all_freq += int(all_freq)
        count += 1
        if count == c:
            if first:
                # felételezem, hogy a használatanem volt kevesebb az első x évben, mint később
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


def get_plot(freq_ls, txt_type, line_name):
    years = [item[0] for item in freq_ls]
    freq = [(int(item[1])/int(item[2]))*100 for item in freq_ls]
    line_type = LINES[txt_type][line_name.upper()]
    plt.plot(years, freq, label=line_name, color=line_type[0], linestyle=line_type[1])


def process(inp, interval):
    for i, fl in enumerate(inp):
        freq_ls = []
        fl = fl.split('\n')
        past_type = fl.pop(0).replace('# ', '').split(',')
        for line in fl:
            line = line.strip()
            if line == '':
                continue
            line = line.split('\t')
            freq_ls.append((line[0], line[1], line[2]))
        freq_ls = split_years(freq_ls, interval)
        get_plot(freq_ls, past_type[0], past_type[1])
    plt.legend()
    plt.show()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='Path to file', nargs='+')
    parser.add_argument('-i', '--interval', help='Split timeline rate', nargs='?', default=40, type=int)

    args = parser.parse_args()
    files = []

    for p in args.filepath:
        poss_files = glob(p)
        poss_files = [os.path.abspath(x) for x in poss_files]
        files += poss_files

    return {'files': files, 'interval': args.interval}


def main():
    args = get_args()
    inp = read(args['files'])
    process(inp, args['interval'])


if __name__ == '__main__':
    main()
