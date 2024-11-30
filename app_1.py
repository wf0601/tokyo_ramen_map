from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import random

app = Flask(__name__)

# Load data
ramen_data_path = os.path.join('data', 'tokyo_ramen_restaurants_all_info.csv')
ramen_data = pd.read_csv(ramen_data_path)
print(len(ramen_data))
# Ensure 'visited' column exists
if 'visited' not in ramen_data.columns:
    ramen_data['visited'] = False

sushi_data_path = os.path.join('data', 'tokyo_sushi_restaurants_all_info.csv')
sushi_data = pd.read_csv(sushi_data_path)
print(len(sushi_data))
# Ensure 'visited' column exists
if 'visited' not in sushi_data.columns:
    sushi_data['visited'] = False

unagi_data_path = os.path.join('data', 'tokyo_unagi_restaurants_all_info.csv')
unagi_data = pd.read_csv(unagi_data_path)
print(len(unagi_data))
# Ensure 'visited' column exists
if 'visited' not in unagi_data.columns:
    unagi_data['visited'] = False


# Convert geo-coordinates
ramen_data[['latitude', 'longitude']] = ramen_data['geo_coordinates'].str.split(',', expand=True).astype(float)
sushi_data[['latitude', 'longitude']] = sushi_data['geo_coordinates'].str.split(',', expand=True).astype(float)
unagi_data[['latitude', 'longitude']] = unagi_data['geo_coordinates'].str.split(',', expand=True).astype(float)

@app.route('/ramen')
def index_ramen():
    # Generate marker data
    markers = []
    for idx, row in ramen_data.iterrows():
        icon_color = 'red' if row['visited'] else 'blue'
        markers.append({
            'location': [row['latitude'], row['longitude']],
            'rating': row['rating'],
            #'popup': f"{row['name']} {row['rating']}<br><input type='checkbox' id='checkbox_{idx}' onchange='toggleVisited({idx})' {'checked' if row['visited'] else ''}> Visited",
            'popup':f"""
    {row['name']} {row['rating']}<br>
    <input type='checkbox' id='checkbox_{idx}' onchange='toggleVisited({idx})' {'checked' if row['visited'] else ''}> Visited<br>
    <a href="#" onclick="openReviewModal({idx}, '{row['name']}')">My Note</a>
""",
            
            'icon_color': icon_color,
            'idx': idx
        })
    # Pass the marker data to the template
    return render_template('ramen.html', markers=markers)

@app.route('/sushi')
def index_sushi():
    # Generate marker data
    markers = []
    for idx, row in sushi_data.iterrows():
        icon_color = 'red' if row['visited'] else 'blue'
        markers.append({
            'location': [row['latitude'], row['longitude']],
            'popup': f"{row['name']} {row['rating']}<br><input type='checkbox' id='checkbox_{idx}' onchange='toggleVisited({idx})' {'checked' if row['visited'] else ''}> Visited",
            'icon_color': icon_color,
            'idx': idx
        })

    # Pass the marker data to the template
    return render_template('sushi.html', markers=markers)

@app.route('/unagi')
def index_unagi():
    # Generate marker data
    markers = []
    visited_count = unagi_data['visited'].sum()
    for idx, row in unagi_data.iterrows():
        icon_color = 'red' if row['visited'] else 'blue'
        markers.append({
            'location': [row['latitude'], row['longitude']],
            'popup': f"{row['name']} {row['rating']}<br><input type='checkbox' id='checkbox_{idx}' onchange='toggleVisited({idx})' {'checked' if row['visited'] else ''}> Visited",
            'icon_color': icon_color,
            'idx': idx
        })

    # Pass the marker data to the template
    return render_template('unagi.html', markers=markers,visited_count = visited_count)

@app.route('/toggle_visited/ramen/<int:idx>', methods=['POST'])
def toggle_visited_ramen(idx):
    # Toggle the visited status
    if idx >= len(ramen_data):  # Handle invalid index
        return jsonify(success=False, error="Invalid index"), 400

    ramen_data.at[idx, 'visited'] = not ramen_data.at[idx, 'visited']
    ramen_data.to_csv(ramen_data_path, index=False)
    return jsonify(success=True, visited=ramen_data.at[idx, 'visited'])

@app.route('/toggle_visited/sushi/<int:idx>', methods=['POST'])
def toggle_visited_sushi(idx):
    # Toggle the visited status
    if idx >= len(sushi_data):  # Handle invalid index
        return jsonify(success=False, error="Invalid index"), 400

    sushi_data.at[idx, 'visited'] = not sushi_data.at[idx, 'visited']
    sushi_data.to_csv(sushi_data_path, index=False)
    visited_status = bool(sushi_data.at[idx, 'visited'])
    return jsonify(success=True, visited=visited_status)
    # return jsonify(success=True, visited=sushi_data.at[idx, 'visited'])

@app.route('/toggle_visited/unagi/<int:idx>', methods=['POST'])
def toggle_visited_unagi(idx):
    # Toggle the visited status
    if idx >= len(unagi_data):  # Handle invalid index
        return jsonify(success=False,error="Invalid index"), 400

    unagi_data.at[idx, 'visited'] = not unagi_data.at[idx, 'visited']
    unagi_data.to_csv(unagi_data_path, index=False)
    visited_status = bool(unagi_data.at[idx, 'visited'])
    return jsonify(success=True, visited=visited_status)

@app.route('/unagi/count')
def unagi_count():
    visited_count = unagi_data['visited'].sum()  # Count visited restaurants
    return jsonify(success=True, visited_count=int(visited_count))

@app.route('/save_review/ramen/<int:idx>', methods=['POST'])
def save_review_ramen(idx):
    if idx >= len(ramen_data):  # Handle invalid index
        return jsonify(success=False, error="Invalid index"), 400

    data = request.get_json()
    review = data.get('review', '')

    # Ensure the 'reviews' column exists
    if 'reviews' not in ramen_data.columns:
        ramen_data['reviews'] = ''  # Create the column if it doesn't exist

    # Convert the existing reviews to a string if it's not already
    existing_reviews = ramen_data.at[idx, 'reviews']
    if pd.isna(existing_reviews):  # Check if it's NaN
        existing_reviews = ''  # Treat NaN as an empty string

    # Append the new review to the existing reviews
    if existing_reviews:
        ramen_data.at[idx, 'reviews'] = existing_reviews + f"; {review}"  # Append with a semicolon
    else:
        ramen_data.at[idx, 'reviews'] = review  # Set the review

    ramen_data.to_csv(ramen_data_path, index=False)  # Save the updated DataFrame
    return jsonify(success=True)

@app.route('/')
def landing_page():
    ramen_visit_cnt = ramen_data['visited'].sum()
    unagi_visit_cnt = unagi_data['visited'].sum()
    sushi_visit_cnt = sushi_data['visited'].sum()
    
    unvisited_ramen = ramen_data[ramen_data['visited'] == False]
    unvisited_unagi = unagi_data[unagi_data['visited'] == False]
    unvisited_sushi = sushi_data[sushi_data['visited'] == False]

    selected_ramen = unvisited_ramen.sample(n=1).iloc[0] if not unvisited_ramen.empty else None
    selected_unagi = unvisited_unagi.sample(n=1).iloc[0] if not unvisited_unagi.empty else None
    selected_sushi = unvisited_sushi.sample(n=1).iloc[0] if not unvisited_sushi.empty else None
    selected_shops = [selected_ramen, selected_unagi, selected_sushi]
    # Filter out None values
    selected_shops = [shop for shop in selected_shops if shop is not None]

    # Randomly select one shop if there are any available
    selected_shop = random.choice(selected_shops)
    # print(selected_unagi['name'])
    return render_template('landing.html',
                           ramen_visit_cnt = ramen_visit_cnt,
                           unagi_visit_cnt = unagi_visit_cnt,
                           sushi_visit_cnt = sushi_visit_cnt,
                           selected_shop=selected_shop)
    
@app.route('/search_restaurants')
def search_restaurants():
    station_name = request.args.get('station', '').lower()
    
    # Filter restaurants based on the station name
    filtered_ramen = ramen_data[ramen_data['station'].str.lower().str.contains(station_name, na=False)]
    filtered_unagi = unagi_data[unagi_data['station'].str.lower().str.contains(station_name, na=False)]
    filtered_sushi = sushi_data[sushi_data['station'].str.lower().str.contains(station_name, na=False)]

    # Combine results
    restaurants = []
    for idx, row in filtered_ramen.iterrows():
        restaurants.append({'name': row['name'], 'station': row['station'], 'rating': row['rating']})
    for idx, row in filtered_unagi.iterrows():
        restaurants.append({'name': row['name'], 'station': row['station'], 'rating': row['rating']})
    for idx, row in filtered_sushi.iterrows():
        restaurants.append({'name': row['name'], 'station': row['station'], 'rating': row['rating']})
        
    top_restaurants = sorted(restaurants, key=lambda x: x['rating'], reverse=True)[:3]    

    return jsonify(restaurants=top_restaurants)
if __name__ == '__main__':
    app.run(debug=True,port=5002)