FROM ubuntu:22.04 as builder

# 依存パッケージのインストール
RUN apt-get -y update && apt-get install -y python3 python3-pip pdal

# Pythonの依存パッケージのインストール
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# ワーキングディレクトリを/root/workspaceに設定
WORKDIR /root/workspace
