import json
import sys

import matplotlib.pyplot as plt
import numpy as np


def bounding_rect(inputfile):
    """2D点群をプロットした画像の作成

    Args:
        inputfile (string): 2D点群JSONファイルのパス
    """
    with open(inputfile, "r") as file:
        geojson = json.load(file)
    print(geojson)
    np_data = np.array(geojson)
    print("Point Num:", len(np_data.tolist()))

    # 結果画像出力
    plt.plot(np_data[:, 0], np_data[:, 1], "b-", alpha=0.7, label="concave")
    plt.savefig("concave.png")


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2:
        bounding_rect(str(args[1]))
    else:
        print("Usage: python " + args[0] + " [input file]")
