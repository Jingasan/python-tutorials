import os
import sys
import json
import numpy as np
import pandas as pd
import laspy
import matplotlib.pyplot as plt
import alphashape
from shapely.geometry import Polygon


def readlas(inputfile):
    las = laspy.read(inputfile)
    print(las.X)
    data = pd.DataFrame(las.points.array)
    data.columns = (x.lower() for x in data.columns)
    data.loc[:, ["x", "y", "z"]] *= las.header.scales
    data.loc[:, ["x", "y", "z"]] += las.header.offsets
    dataset = np.stack([data.x, data.y], axis=1)

    alpha = 5
    shp = alphashape.alphashape(dataset, alpha)
    alpha_shape_coords = np.array(shp.exterior.coords)

    # plt.plot(dataset[:, 0], dataset[:, 1], 'o', markersize=1, label='Points')
    # plt.plot(alpha_shape_coords[:, 0], alpha_shape_coords[:, 1], 'r-', alpha=0.7, label='AlphaShape')
    # plt.savefig('7.png')

    polygon = Polygon(alpha_shape_coords)
    simplified_polygon = polygon.simplify(0.01, preserve_topology=True)
    simplified_polygon_coordinates = np.array(simplified_polygon.exterior.coords)

    with open("concave_hull.json", "w") as json_file:
        json.dump(simplified_polygon_coordinates.tolist(), json_file)

    plt.plot(dataset[:, 0], dataset[:, 1], "o", markersize=1, label="Points")
    plt.plot(
        simplified_polygon_coordinates[:, 0],
        simplified_polygon_coordinates[:, 1],
        "r-",
        alpha=0.7,
        label="AlphaShape",
    )
    plt.savefig("concave_hull.png")


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2:
        readlas(str(args[1]))
    else:
        print("Usage: python " + args[0] + " [input file]")
