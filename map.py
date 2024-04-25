import folium


def ship_map():
    # Create a base map
    world_map = folium.Map(location=[23.6978, 120.9605], zoom_start=3, tiles='CartoDB dark_matter')

    arriving_ships = {
        'start': {'name': 'Ship A', 'latitude': -20.0, 'longitude': 118.0},
        'end': {'name': 'TWKHH', 'latitude': 22.5529, 'longitude': 120.2851}
    }
    departing_ships = {
        'start': {'name': 'Ship B', 'latitude': 35.0, 'longitude': 129.0},
        'end': {'name': 'TWKHH', 'latitude': 22.5529, 'longitude': 120.2851}
    }

    arriving_group = folium.FeatureGroup(name='Arriving Ships', show=True)
    departing_group = folium.FeatureGroup(name='Departing Ships', show=True)

    for ship in [arriving_ships['start']]:
        folium.CircleMarker(
            location=[ship['latitude'], ship['longitude']],
            radius=1,
            color='yellow',
            fill=True,
            fill_color='yellow',
            # popup=ship['name']
        ).add_to(arriving_group)

    for ship in [departing_ships['start']]:
        folium.CircleMarker(
            location=[ship['latitude'], ship['longitude']],
            radius=0.5,
            color='red',
            fill=True,
            fill_color='red',
            # popup=ship['name']
        ).add_to(departing_group)
    # Add feature groups to the map

    arriving_group.add_to(world_map)
    departing_group.add_to(world_map)

    # Add layer control to enable toggling between ship types
    folium.LayerControl().add_to(world_map)

    # Save the map as an HTML file
    world_map.save('templates/map_base.html')
