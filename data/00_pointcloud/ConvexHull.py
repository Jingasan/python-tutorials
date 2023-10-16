import os
import sys
import json
import numpy as np
import pandas as pd
import laspy
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt


def readlas(inputfile):
    las = laspy.read(inputfile)
    print(las.X)
    data = pd.DataFrame(las.points.array)
    data.columns = (x.lower() for x in data.columns)
    data.loc[:, ["x", "y", "z"]] *= las.header.scales
    data.loc[:, ["x", "y", "z"]] += las.header.offsets
    dataset = np.stack([data.x, data.y], axis=1)

    # plt.scatter(dataset[:, 0], dataset[:, 1])
    # plt.savefig('3.png')

    hull = ConvexHull(dataset)
    points = hull.points
    hull_points = points[hull.vertices]
    print(hull_points)

    hp = np.vstack((hull_points, hull_points[0]))

    with open("convex_hull.json", "w") as json_file:
        json.dump(hp.tolist(), json_file)

    plt.plot(points[:, 0], points[:, 1], "o", markersize=1, label="Points")
    plt.plot(hp[:, 0], hp[:, 1], "r-")
    plt.savefig("convex_hull.png")

    # print(dataset.tolist())

    # with laspy.open(inputfile) as file:
    #     print('Points from Header:', file.header.point_count)
    #     print(file.x)


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2:
        readlas(str(args[1]))
    else:
        print("Usage: python " + args[0] + " [input file]")
