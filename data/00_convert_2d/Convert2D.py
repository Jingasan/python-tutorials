import json
import sys

import laspy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN


def convert_2d(inputfile):
    """LAS/LAZ点群の2D点群化

    Args:
        inputfile (string): 2D化するLAS/LAZファイルのパス
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
    grid_size = 0.05  # グリッドサイズ[m]
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

    # DNSCANによるノイズ点除去
    epsilon = 0.1  # ε-neighborhoodの半径
    min_samples = 2  # クラスターを形成するために必要な最小サンプル数
    dbscan = DBSCAN(eps=epsilon, min_samples=min_samples)  # DBSCANモデルを作成
    dbscan.fit(np_pointcloud_2d)  # 点群をクラスタリング
    noise_mask = dbscan.labels_ == -1  # ノイズ点を識別
    np_pointcloud_2d = np_pointcloud_2d[~noise_mask]  # ノイズ以外の点を取得
    print("Downsampled Point Num:", len(np_pointcloud_2d.tolist()))

    # JSON出力
    with open("points2d.json", "w") as file:
        json.dump(np_pointcloud_2d.tolist(), file)

    # 結果画像出力
    plt.plot(np_pointcloud_2d[:, 0], np_pointcloud_2d[:, 1], "o", markersize=1, label="Points")
    plt.savefig("points2d.png")


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2:
        convert_2d(str(args[1]))
    else:
        print("Usage: python " + args[0] + " [input file]")
