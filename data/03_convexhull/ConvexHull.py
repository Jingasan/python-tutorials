import json
import sys

import laspy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull


def convex_hull(inputfile):
    """LAS/LAZ点群から2Dの凸包を求める関数

    Args:
        inputfile (string): 入力LAS/LAZファイル
    """

    # LAS/LAZ点群の読み込み
    las = laspy.read(inputfile)

    # 点群のXY座標群の取得
    data = pd.DataFrame(las.points.array)
    data.columns = (x.lower() for x in data.columns)
    data.loc[:, ["x", "y", "z"]] *= las.header.scales
    data.loc[:, ["x", "y", "z"]] += las.header.offsets
    np_pointcloud_2d = np.stack([data.x, data.y]).transpose()
    print("Input Point Num:", las.header.point_count)

    # 2D点群のグリッドサンプリング
    grid_size = 0.1  # グリッドサイズ[m]
    sampled_points = {}  # 間引いた点を保持する辞書
    # 各点をグリッドに割り当てる
    for point in np_pointcloud_2d:
        cell_x = int(point[0] // grid_size)
        cell_y = int(point[1] // grid_size)
        cell_key = (cell_x, cell_y)
        # グリッド内に１つ点を設定する（すでに点がある場合は無視）
        if cell_key not in sampled_points:
            sampled_points[cell_key] = point
    # 辞書の値を配列型 → Numpyの配列型に変換
    sampled_points = list(sampled_points.values())
    np_pointcloud_2d = np.array(sampled_points)
    print("Downsampled Point Num:", len(np_pointcloud_2d.tolist()))

    # 凸包の計算
    hull = ConvexHull(np_pointcloud_2d)
    points = hull.points
    hull_points = points[hull.vertices]
    np_convexhull = np.vstack((hull_points, hull_points[0]))
    print("Convex Point Num:", len(np_convexhull.tolist()))

    # JSON出力
    with open("convex_hull.json", "w") as json_file:
        json.dump(np_convexhull.tolist(), json_file)

    # 結果画像出力
    plt.plot(np_pointcloud_2d[:, 0], np_pointcloud_2d[:, 1], "o", markersize=1, label="Points")
    plt.plot(np_convexhull[:, 0], np_convexhull[:, 1], "r-", alpha=0.7, label="ConvexHull")
    plt.savefig("convex_hull.png")


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2:
        convex_hull(str(args[1]))
    else:
        print("Usage: python " + args[0] + " [input file]")
