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


def process(inp=None):
    colors = ['red', 'yellow', 'green', 'brown']
    # TODO: az impf és a pf esetében is egyszerre kell beolvasni a 4 gyak_dokumentumot
    # TODO: --> és for ciklussal legenerálni a plot-ot
    years = [elem[0] for elem in inp]
    # freq = [elem[1] for elem in inp]
    for i in range(3):
        freq = [randint(1, 20) for elem in inp]
        plt.plot(years, freq, label='vonalak címe', color=colors[i])

    plt.xlabel('Évek')
    plt.ylabel('Százalékos arány')
    plt.title('A diagram címe')
    plt.legend()
    plt.show()
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
    # args = get_args()
    # inp = read(args['files'])
    inp = [('1550-1575', 5), ('1575-1600', 7), ('1600-1625', 10), ('1625-1650', 7), ('1650-1675', 3)]
    outp = process(inp)


if __name__ == '__main__':
    main()


# def example_one():
#     # Create data
#     N = 500
#     x = np.random.rand(N)
#     y = np.random.rand(N)
#     colors = (0,0,0)
#     area = np.pi*3
#
#     # Plot
#     # plt.scatter(x, y)  # , s=area, c=colors, alpha=0.5)
#     plt.scatter(100, 200)  # , s=area, c=colors, alpha=0.5)
#     plt.title('Scatter plot pythonspot.com')
#     plt.plot(x,y, '-o')
#     plt.plot(x+30,y +20, '-o')
#     # plt.xlabel('x')
#     # plt.ylabel('y')
#     plt.show()
#
#
# def example_two():
#     import numpy as np
#     import matplotlib.pyplot as plt
#
#     x, y = np.random.random(size=(2, 10))
#
#     for i in range(0, len(x), 2):
#         plt.plot(x[i:i + 2], y[i:i + 2], 'ro-')
#
#     plt.show()
#
#
# def example_three():
#     # scatter plot with groups --> ez is kelleni fog
#     # Create data
#     N = 60
#     g1 = (0.6 + 0.6 * np.random.rand(N), np.random.rand(N))
#     g2 = (0.4 + 0.3 * np.random.rand(N), 0.5 * np.random.rand(N))
#     g3 = (0.3 * np.random.rand(N), 0.3 * np.random.rand(N))
#
#     data = (g1, g2, g3)
#     colors = ("red", "green", "blue")
#     groups = ("coffee", "tea", "water")
#
#     # Create plot
#     fig = plt.figure()
#     ax = fig.add_subplot(1, 1, 1, axisbg="1.0")
#
#     for data, color, group in zip(data, colors, groups):
#         x, y = data
#         ax.scatter(x, y, alpha=0.8, c=color, edgecolors='none', s=30, label=group)
#
#     plt.title('Matplot scatter plot')
#     plt.legend(loc=2)
#     plt.show()
#
#
# example_three()