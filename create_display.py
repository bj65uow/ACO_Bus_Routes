def generate_map(joined_data):
    map_figure = joined_data.explore(tiles='https://api.mapbox.com/styles/v1/bj65/clrqu3sys004n01r15x8n4qb1/tiles/256/{z}/{x}/{y}@2x?access_token=sk.eyJ1IjoiYmo2NSIsImEiOiJjbHJxdm5oODkwN2c5MmpxbnR2aWF6YWk2In0.YH9URMfcHwNN2daFqv8UvQ', attr='MapBox')  # Requires folium, matplotlib, and mapclassify
    return map_figure

def generate_map_colour(joined_data, colour):
    map_figure = joined_data.explore(color=colour, tiles='https://api.mapbox.com/styles/v1/bj65/clrqu3sys004n01r15x8n4qb1/tiles/256/{z}/{x}/{y}@2x?access_token=sk.eyJ1IjoiYmo2NSIsImEiOiJjbHJxdm5oODkwN2c5MmpxbnR2aWF6YWk2In0.YH9URMfcHwNN2daFqv8UvQ', attr='MapBox')  # Requires folium, matplotlib, and mapclassify
    return map_figure