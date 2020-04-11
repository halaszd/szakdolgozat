import matplotlib.pyplot as plt
from glob import glob
import argparse
import os


COLORS = {'PERF. + VALA': 'red',
          'PERF. + VOLT': 'yellow',
          'IMP. + VALA': 'green',
          'IMP. + VOLT': 'brown'}

TITLES = {}

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
                new_freq_ls.append((freq_ls[0][0], sum_pfreq, sum_all_freq))
                first = False
            new_freq_ls.append((year, sum_pfreq, sum_all_freq))
            sum_pfreq = 0
            sum_all_freq = 0
            count = 0
        if i == len(freq_ls)-1 and count > 0:
            new_freq_ls.append((year, sum_pfreq, sum_all_freq))
    return new_freq_ls


def get_plot(freq_ls, line_name):
    years = [item[0] for item in freq_ls]
    freq = [(int(item[1])/int(item[2]))*100 for item in freq_ls]
    plt.plot(years, freq, label=line_name, color=COLORS[line_name.upper()])


def process(inp):
    for i, fl in enumerate(inp):
        freq_ls = []
        fl = fl.split('\n')
        plt_line_name = ' '.join(fl.pop(0).split()[1:])
        for line in fl:
            line = line.strip()
            if line == '':
                continue
            line = line.split('\t')
            freq_ls.append((line[0], line[1], line[2]))
        freq_ls = split_years(freq_ls, 40)
        get_plot(freq_ls, plt_line_name)
    plt.title('Cím')
    plt.legend()
    plt.show()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='Path to file', nargs='+')

    args = parser.parse_args()
    files = []

    for p in args.filepath:
        poss_files = glob(p)
        poss_files = [os.path.abspath(x) for x in poss_files]
        files += poss_files

    return {'files': files}


def main():
    args = get_args()
    inp = read(args['files'])
    process(inp)


if __name__ == '__main__':
    main()
