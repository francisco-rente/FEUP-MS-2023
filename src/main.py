import contextily as cx
import geopandas as gpd
import matplotlib.pyplot as plt

df = gpd.read_file('../datasets/BGRI2021_1312.gpkg')
ax = df.plot()
cx.add_basemap(ax, crs=df.crs.to_string())

plt.show()
