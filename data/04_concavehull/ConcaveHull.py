import json
import sys

import alphashape
import laspy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely.geometry import Polygon
from sklearn.cluster import DBSCAN


def concaveHull(inputfile):
    """LAS/LAZ点群から2Dの凹包を求める関数

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

    # # 2D点群のグリッドサンプリング
    # grid_size = 0.1  # グリッドサイズ[m]
    # sampled_points = {}  # 間引いた点を保持する辞書
    # # 各点をグリッドに割り当てる
    # for point in np_pointcloud_2d:
    #     cell_x = int(point[0] // grid_size)
    #     cell_y = int(point[1] // grid_size)
    #     cell_key = (cell_x, cell_y)
    #     # グリッド内に１つ点を設定する（すでに点がある場合は無視）
    #     if cell_key not in sampled_points:
    #         sampled_points[cell_key] = point
    # # 辞書の値を配列型 → Numpyの配列型に変換
    # sampled_points = list(sampled_points.values())
    # np_pointcloud_2d = np.array(sampled_points)
    # print("Downsampled Point Num:", len(np_pointcloud_2d.tolist()))

    # # DNSCANによるノイズ点除去
    # epsilon = 0.1  # ε-neighborhoodの半径
    # min_samples = 2  # クラスターを形成するために必要な最小サンプル数
    # dbscan = DBSCAN(eps=epsilon, min_samples=min_samples)  # DBSCANモデルを作成
    # dbscan.fit(np_pointcloud_2d)  # 点群をクラスタリング
    # noise_mask = dbscan.labels_ == -1  # ノイズ点を識別
    # np_pointcloud_2d = np_pointcloud_2d[~noise_mask]  # ノイズ以外の点を取得
    # print("Downsampled Point Num:", len(np_pointcloud_2d.tolist()))

    # 凹包の計算
    alpha = 5
    alphashape_concavehull = alphashape.alphashape(np_pointcloud_2d, alpha)
    np_concavehull = np.array(alphashape_concavehull.exterior.coords)
    print("Concave Point Num:", len(np_concavehull.tolist()))

    # 凹包点群の単純化
    shapely_polygon = Polygon(np_concavehull)
    shaply_simplified_polygon = shapely_polygon.simplify(0.1, preserve_topology=True)
    np_concavehull = np.array(shaply_simplified_polygon.exterior.coords)
    print("Concave Point Num:", len(np_concavehull.tolist()))

    # JSON出力
    with open("concave_hull.json", "w") as file:
        json.dump(np_concavehull.tolist(), file)

    # 結果画像出力
    plt.plot(np_pointcloud_2d[:, 0], np_pointcloud_2d[:, 1], "o", markersize=1, label="Points")
    plt.plot(np_concavehull[:, 0], np_concavehull[:, 1], "r-", alpha=0.7, label="ConcaveHull")
    plt.savefig("concave_hull.png")


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2:
        concaveHull(str(args[1]))
    else:
        print("Usage: python " + args[0] + " [input file]")
