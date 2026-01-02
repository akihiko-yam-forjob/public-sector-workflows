import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import point
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
# ---------------------------------------------------------
# データの読み込み
# ---------------------------------------------------------
# シェープファイルの読み込み (500mメッシュデータ)
gdf_pop = gpd.read_file("500m_mesh_2018_01_cut.shp")

# データの先頭を確認（インタラクティブ実行時の確認用）
print(gdf_pop.head())

# ---------------------------------------------------------
# データ処理
# ---------------------------------------------------------
# 2時点間の人口減少率の計算
# 式: (2050年予測 - 2015年実績) / 2015年実績
gdf_pop['decrease_rate'] = (gdf_pop['PTN_2050'] - gdf_pop['PTN_2015']) / gdf_pop['PTN_2015']

# ---------------------------------------------------------
# 可視化 1: 地図へのプロット
# ---------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 10))

# 地図のアスペクト比を保持（歪みを防ぐ設定）
ax.set_aspect('equal')
ax.set_title('Population Decrease Rate (2015-2050)')

# 減少率の閾値設定（分析の目安として定義）
thresholds = [-1.0, 0.2, 0.8, 2.235] 
colors = ['green', 'yellow', 'red', 'purple']

# GeoDataFrameのプロット
# column引数を使って減少率(decrease_rate)で色分け
# cmapには視認性の良い 'RdYlGn' (赤-黄-緑) などを指定
gdf_pop.plot(
    ax=ax,
    column='decrease_rate',
    cmap='RdYlGn',       # エラー回避のため文字列で指定
    linewidth=0.1,       # 境界線を細くして見やすく調整
    edgecolor='gray',
    legend=True,         # 凡例を表示
    legend_kwds={'label': "Decrease Rate"}
)

plt.show()

# ---------------------------------------------------------
# 可視化 2: ヒストグラムによる分布確認
# ---------------------------------------------------------
# 減少率の分布状況を確認
plt.figure(figsize=(8, 6))
plt.hist(gdf_pop['decrease_rate'].dropna(), bins=20, edgecolor='black')

plt.xlabel('Decrease Rate')
plt.ylabel('Count')
plt.title('Histogram of Decrease Rate')
plt.grid(True)
plt.show()