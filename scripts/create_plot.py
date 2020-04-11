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


def get_plot(freq_matrix):
    colors = ['red', 'yellow', 'green', 'brown']
    # TODO: az impf és a pf esetében is egyszerre kell beolvasni a 4 gyak_dokumentumot
    # TODO: --> és for ciklussal legenerálni a plot-ot
    for i, freq_ls in enumerate(freq_matrix):
        print(freq_ls)
        years = [item[0] for item in freq_ls]
        freq = [randint(1, 20) for elem in inp]
        for tup in freq_ls:
            plt.plot(years, freq, label='vonalak címe', color=colors[i])
            # plt.plot(years, poly_y, color=colors[i])
            plt.xlabel('Évek')
            plt.ylabel('Százalékos arány')
            plt.title('A diagram címe')
            plt.legend()
    plt.show()


def process(inp):
    freq_lss = []
    for fl in inp:
        freq_ls = []
        for line in fl.split('\n'):
            line = line.strip()
            if line == '':
                continue
            line = line.split('\t')
            if line:
                freq_ls.append((line[0], line[1]))
        freq_lss.append(freq_ls)
    get_plot(freq_lss)
    return 0


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
