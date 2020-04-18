#! /usr/bin/env python3
import matplotlib.pyplot as plt
import argparse
import sys
sys.path.append('../')
from scripts.common import str2bool


LINES = {'inform.':
             {'perf.':
                  {'vala': ('red', '-'),
                   'volt': ('yellow', '-')},
              'imp.':
                  {'vala': ('green', '-'),
                   'volt': ('brown', '-')},
              'neutr.':
                  {'vala': ('red', '-'),
                   'volt': ('yellow', '-')}},
         'form.':
             {'perf.':
                  {'vala': ('red', '--'),
                   'volt': ('yellow', '--')},
              'imp.':
                  {'vala': ('green', '--'),
                   'volt': ('brown', '--')},
              'neutr.':
                  {'vala': ('red', '-'),
                   'volt': ('yellow', '-')}}}


def read(inp):
    for fl in inp:
        print(fl)
        with open(fl, 'r', encoding='utf-8') as f:
            yield f.read()


def split_years(freq_ls, is_mixed, c):
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
    freq = [(float(item[1])/float(item[2]))*100 for item in freq_ls]
    line_type = LINES[txt_type[0]][txt_type[1]][txt_type[2]]
    plt.plot(years, freq, label=line_name.upper(), color=line_type[0], linestyle=line_type[1])


def process(inp, interval, is_mixed):
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
        freq_ls = split_years(freq_ls, is_mixed, interval)
        get_plot(freq_ls, past_type, '{} {} + {}'.format(past_type[0], past_type[1], past_type[2]))
    plt.legend()
    plt.show()


def get_args():
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
