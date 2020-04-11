import matplotlib.pyplot as plt
from glob import glob
import argparse
import os


def read(inp):
    for fl in inp:
        with open(fl, 'r', encoding='utf-8') as f:
            yield f.read()


def get_title_label(xlabel='', ylabel='', title=''):
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)


def get_plot(freq_ls, clr):
    years = [item[0] for item in freq_ls]
    freq = [int(item[1]) for item in freq_ls]
    plt.plot(years, freq, label='vonalak címe', color=clr)


def split_years(freq_ls, c=1):
    count = 0
    sum_freq = 0
    new_freq_ls = [freq_ls.pop(0)]
    for i, (year, freq) in enumerate(freq_ls):
        sum_freq += int(freq)
        count += 1
        if count == c:
            new_freq_ls.append((year, sum_freq))
            sum_freq = 0
            count = 0
        if i == len(freq_ls)-1 and count > 0:
            new_freq_ls.append((year, sum_freq))
    return new_freq_ls


def process(inp):
    colors = ['red', 'yellow', 'green', 'brown']
    for i, fl in enumerate(inp):
        freq_ls = []
        for line in fl.split('\n'):
            line = line.strip()
            if line == '':
                continue
            line = line.split('\t')
            freq_ls.append((line[0], line[1]))
        freq_ls = split_years(freq_ls, 1)
        get_plot(freq_ls, colors[i])
    get_title_label('Cím', 'x leírás', 'y leírás')
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
