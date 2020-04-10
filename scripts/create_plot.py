import numpy as np
import matplotlib.pyplot as plt

def example_one():
    # Create data
    N = 500
    x = np.random.rand(N)
    y = np.random.rand(N)
    colors = (0,0,0)
    area = np.pi*3

    # Plot
    # plt.scatter(x, y)  # , s=area, c=colors, alpha=0.5)
    plt.scatter(100, 200)  # , s=area, c=colors, alpha=0.5)
    plt.title('Scatter plot pythonspot.com')
    plt.plot(x,y, '-o')
    plt.plot(x+30,y +20, '-o')
    # plt.xlabel('x')
    # plt.ylabel('y')
    plt.show()


def example_two():
    import numpy as np
    import matplotlib.pyplot as plt

    x, y = np.random.random(size=(2, 10))

    for i in range(0, len(x), 2):
        plt.plot(x[i:i + 2], y[i:i + 2], 'ro-')

    plt.show()


def example_three():
    # scatter plot with groups --> ez is kelleni fog
    # Create data
    N = 60
    g1 = (0.6 + 0.6 * np.random.rand(N), np.random.rand(N))
    g2 = (0.4 + 0.3 * np.random.rand(N), 0.5 * np.random.rand(N))
    g3 = (0.3 * np.random.rand(N), 0.3 * np.random.rand(N))

    data = (g1, g2, g3)
    colors = ("red", "green", "blue")
    groups = ("coffee", "tea", "water")

    # Create plot
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, axisbg="1.0")

    for data, color, group in zip(data, colors, groups):
        x, y = data
        ax.scatter(x, y, alpha=0.8, c=color, edgecolors='none', s=30, label=group)

    plt.title('Matplot scatter plot')
    plt.legend(loc=2)
    plt.show()


example_three()