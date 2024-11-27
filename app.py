from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Load data
data_path = os.path.join('data', 'tokyo_ramen_restaurants_all_info.csv')
data = pd.read_csv(data_path)

# Ensure 'visited' column exists
if 'visited' not in data.columns:
    data['visited'] = False

# Convert geo-coordinates
data[['latitude', 'longitude']] = data['geo_coordinates'].str.split(',', expand=True).astype(float)

@app.route('/')
def index():
    # Generate marker data
    markers = []
    for idx, row in data.iterrows():
        icon_color = 'red' if row['visited'] else 'blue'
        markers.append({
            'location': [row['latitude'], row['longitude']],
            'popup': f"{row['name']}<br><input type='checkbox' id='checkbox_{idx}' onchange='toggleVisited({idx})' {'checked' if row['visited'] else ''}> Visited",
            'icon_color': icon_color,
            'idx': idx
        })

    # Pass the marker data to the template
    return render_template('index.html', markers=markers)

@app.route('/toggle_visited/<int:idx>', methods=['POST'])
def toggle_visited(idx):
    # Toggle the visited status
    if idx >= len(data):  # Handle invalid index
        return jsonify(success=False, error="Invalid index"), 400

    data.at[idx, 'visited'] = not data.at[idx, 'visited']
    data.to_csv(data_path, index=False)
    return jsonify(success=True, visited=data.at[idx, 'visited'])

if __name__ == '__main__':
    app.run(debug=True)