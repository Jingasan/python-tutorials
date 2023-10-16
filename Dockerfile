FROM ubuntu:22.04 as builder

# 依存パッケージのインストール
RUN apt-get -y update && apt-get install -y python3 python3-pip
RUN pip install numpy pandas matplotlib laspy[lazrs,laszip] scipy alphashape shapely

# ワーキングディレクトリを/homeに設定
WORKDIR /root