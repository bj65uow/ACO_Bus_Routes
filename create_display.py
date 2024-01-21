def generate_map(joined_data):
    map_figure = joined_data.explore()  # Requires folium, matplotlib, and mapclassify
    return map_figure

def generate_map_colour(joined_data, colour):
    map_figure = joined_data.explore(color=colour, tiles='openstreetmap')  # Requires folium, matplotlib, and mapclassify
    return map_figure