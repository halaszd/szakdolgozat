from scipy.interpolate import make_interp_spline, BSpline
import numpy as np
from random import randint
import matplotlib.pyplot as plt
from glob import glob
import argparse
import os


def read(inp):
    for fl in inp:
        with open(fl, 'r', encoding='utf-8') as f:
            yield f.read()


def get_title_label(xlabel, ylabel, title):
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)


def get_plot(freq_ls, clr):
    # TODO: az impf és a pf esetében is egyszerre kell beolvasni a 4 gyak_dokumentumot
    # TODO: --> és for ciklussal legenerálni a plot-ot
    years = [item[0] for item in freq_ls]
    freq = [int(item[1]) for item in freq_ls]
    print(freq)
    plt.plot(years, freq, label='vonalak címe', color=clr)
    # plt.plot(years, poly_y, color=colors[i])


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
        get_plot(freq_ls, colors[i])
    get_title_label('Cím', 'x leírás', 'y leírás')
    plt.legend()
    plt.show()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='Path to file', nargs='+')
    parser.add_argument('-d', '--directory', help='Path of output file(s)', nargs='?', default='../outputs/')
    parser.add_argument('-f', '--ofname', help='Output filename')

    args = parser.parse_args()
    files = []

    for p in args.filepath:
        poss_files = glob(p)
        poss_files = [os.path.abspath(x) for x in poss_files]
        files += poss_files

    return {'outdir': args.directory, 'files': files, 'ofname': args.ofname}


def main():
    # inp = [('1550', 5), ('1575', 7), ('1600', 10), ('1625', 7), ('1650', 3), ('1675', 3)]
    args = get_args()
    inp = read(args['files'])
    process(inp)


if __name__ == '__main__':
    main()
