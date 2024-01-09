from plot_nodes import plot
from create_display import generate_map
import generate_line as gl
from flask import Flask
import geopandas as gpd
import pandas as pd

# Get stops
graph = plot()

# TODO: Update generate_line to use new algorithm
# # Hardcoded route start/end points
# start_point = (graph[graph['ref'] == '2401'])['geometry'].iloc[0]
# end_point = (graph[graph['ref'] == '2169'])['geometry'].iloc[0]

# gl.set_start(start_point, end_point, graph)
# line = gl.run()

# # Get line output
# lines = [line]
# gdf = gpd.GeoDataFrame(geometry=lines)
# graph = pd.concat([graph, gdf])

# Create leaflet
figure = generate_map(graph)

app = Flask(__name__)

# Show map with bus stop info full screen web server
@app.route("/")
def fullscreen():
    return figure.get_root().render()

if __name__ == "__main__":
    app.run(debug=True)