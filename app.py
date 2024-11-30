from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import random
import yaml

app = Flask(__name__)

# Load cuisine mapping from YAML file
def load_cuisine_mapping():
    with open('./config/cuisines.yaml', 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

# Load data for each cuisine based on the YAML configuration
def load_cuisine_data(cuisine_mapping):
    data_frames = {}
    for cuisine, info in cuisine_mapping['cuisines'].items():
        data_file = info['data_file']
        data = pd.read_csv(data_file)
        # Ensure 'visited' column exists
        if 'visited' not in data.columns:
            data['visited'] = False
        # Convert geo-coordinates
        data[['latitude', 'longitude']] = data['geo_coordinates'].str.split(',', expand=True).astype(float)
        data_frames[cuisine] = data
        data_frames[cuisine].to_csv(data_file,index=False)
    return data_frames

# Load the cuisine mapping and data
cuisine_mapping = load_cuisine_mapping()
cuisine_data = load_cuisine_data(cuisine_mapping)

@app.route('/<cuisine>')
def index_cuisine(cuisine):
    if cuisine not in cuisine_mapping['cuisines']:
        return "Cuisine not found", 404

    # Get the data and title from the mapping
    cuisine_info = cuisine_mapping['cuisines'][cuisine]
    data = cuisine_data[cuisine]
    title = cuisine_info['title']
    visited_count = data['visited'].sum() if cuisine == 'unagi' else None

    # Generate marker data
    markers = []
    for idx, row in data.iterrows():
        icon_color = 'red' if row['visited'] else 'blue'
        
        markers.append({
            'location': [row['latitude'], row['longitude']],
            'rating': row['rating'],
            'reviews': row['reviews'] if 'reviews' in row else '',
            'popup': f"""
        {row['name']} {row['rating']}<br>
        <input type='checkbox' id='checkbox_{idx}' onchange='toggleVisited({idx})' {'checked' if row['visited'] else ''}> Visited<br>
        <a href="#" onclick="openReviewModal({idx}, '{row['name']}')">My Note</a>
    """,
            'icon_color': icon_color,
            'idx': idx
        })
        # print(markers[0])

    return render_template('cuisine.html', markers=markers, title=title, visited_count=visited_count, cuisine=cuisine)

@app.route('/toggle_visited/<cuisine>/<int:idx>', methods=['POST'])
def toggle_visited(cuisine, idx):
    if cuisine not in cuisine_mapping['cuisines']:
        return jsonify(success=False, error="Invalid cuisine"), 400

    data = cuisine_data[cuisine]

    # Toggle the visited status
    if idx >= len(data):  # Handle invalid index
        return jsonify(success=False, error="Invalid index"), 400

    data.at[idx, 'visited'] = not data.at[idx, 'visited']
    data.to_csv(cuisine_mapping['cuisines'][cuisine]['data_file'], index=False)  # Save the updated DataFrame
    visited_status = bool(data.at[idx, 'visited'])
    return jsonify(success=True, visited=visited_status)

@app.route('/save_review/<cuisine>/<int:idx>', methods=['POST'])
def save_review(cuisine, idx):
    if cuisine not in cuisine_mapping['cuisines']:
        return jsonify(success=False, error="Invalid cuisine"), 400

    data = cuisine_data[cuisine]

    if idx >= len(data):
        return jsonify(success=False, error="Invalid index"), 400

    review = request.get_json().get('review', '')
    # print(review)

    # Ensure the 'reviews' column exists
    if 'reviews' not in data.columns:
        data['reviews'] = ''  # Create the column if it doesn't exist

    # Save the latest review (overwrite any existing review)
    data.at[idx, 'reviews'] = review

    # Save the updated DataFrame back to the corresponding CSV file
    data.to_csv(cuisine_mapping['cuisines'][cuisine]['data_file'], index=False)  # Save the updated DataFrame
    return jsonify(success=True)

@app.route('/')
def landing_page():
    cuisines = ['ramen', 'unagi', 'sushi']
    
    restaurant_counts = {cuisine: len(cuisine_data[cuisine]) for cuisine in cuisines}
    
    visit_counts = {cuisine: cuisine_data[cuisine]['visited'].sum() for cuisine in cuisines}
    unvisited_shops = {
        cuisine: cuisine_data[cuisine][cuisine_data[cuisine]['visited'] == False] for cuisine in cuisines
    }
    selected_shops = [
        unvisited.sample(n=1).iloc[0] if not unvisited.empty else None 
        for unvisited in unvisited_shops.values()
    ]
    selected_shops = [shop for shop in selected_shops if shop is not None]
    selected_shop = random.choice(selected_shops) if selected_shops else None

    return render_template(
        'landing.html',
        visit_counts=visit_counts,  # Pass the dictionary
        selected_shop=selected_shop,
        restaurant_counts=restaurant_counts # dictionary
    )

@app.route('/search_restaurants')
def search_restaurants():
    station_name = request.args.get('station', '').lower()
    
    # Filter restaurants based on the station name
    restaurants = []
    for cuisine in cuisine_mapping['cuisines']:
        data = cuisine_data[cuisine]
        filtered = data[data['station'].str.lower().str.contains(station_name, na=False)]
        for idx, row in filtered.iterrows():
            restaurants.append({'name': row['name'], 'station': row['station'], 'rating': row['rating']})
        
    top_restaurants = sorted(restaurants, key=lambda x: x['rating'], reverse=True)[:3]    

    return jsonify(restaurants=top_restaurants)

if __name__ == '__main__':
    app.run(debug=True, port=5002)