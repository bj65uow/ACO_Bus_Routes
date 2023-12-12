def generate_map(joined_data):
    map_figure = joined_data.explore()  # Requires folium, matplotlib, and mapclassify
    return map_figure