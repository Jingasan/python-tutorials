import json
import sys

import laspy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely.geometry import MultiPoint


def bounding_rect(inputfile):
    """最小外接矩形の算出

    Args:
        inputdir (string): 最小外接矩形の算出する点群ファイルのパス
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

    point_collection = MultiPoint(np_pointcloud_2d)                 # ShapelyのMultiPointオブジェクトを作成
    min_bounding_rect = point_collection.minimum_rotated_rectangle  # 最小の外接矩形を計算
    np_bounding_rect = np.array(min_bounding_rect.exterior.coords)  # 外接矩形の座標を取得
    print("Rect Point Num:", len(np_bounding_rect.tolist()))
    print(np_bounding_rect)

    # JSON出力
    with open("concave_hull.json", "w") as file:
        json.dump(np_bounding_rect.tolist(), file)

    # 結果画像出力
    plt.plot(np_pointcloud_2d[:, 0], np_pointcloud_2d[:, 1], "o", markersize=1, label="Points")
    plt.plot(np_bounding_rect[:, 0], np_bounding_rect[:, 1], "r-", alpha=0.7, label="Rect")
    plt.savefig("rect.png")


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2:
        bounding_rect(str(args[1]))
    else:
        print("Usage: python " + args[0] + " [input file]")
