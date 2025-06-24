from flask import Flask, jsonify, request
from flask_cors import CORS
import pymongo
import requests
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import certifi


load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError("MONGODB_URI not set in .env file")
try:
    client = pymongo.MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=30000,
            tls=True,
            tlsCAFile=certifi.where()
    )
    db = client['fpl-ai-assistant']  # Database name
    # Test connection
    client.admin.command('ping')
    print("MongoDB connection successful!")
except pymongo.errors.ServerSelectionTimeoutError as e:
    print(f"MongoDB connection failed: {e}")
    raise
except Exception as e:
    print(f"Unexpected error: {e}")
    raise

# FPL API endpoints
FPL_BOOTSTRAP = 'https://fantasy.premierleague.com/api/bootstrap-static/'
FPL_FIXTURES = 'https://fantasy.premierleague.com/api/fixtures/'


def fetch_fpl_data():
    # Check if data is already in MongoDB
    collection = db['bootstrap_data']
    data = list(collection.find().sort('_id', -1).limit(1))
    if data:
        return data[0]['data']

    # Fetch from FPL API
    response = requests.get(FPL_BOOTSTRAP)
    data = response.json()

    # Store in MongoDB
    collection.insert_one({'timestamp': datetime.datetime.now(
        datetime.UTC), 'data': data})
    return data


@app.route('/api/bootstrap', methods=['GET'])
def get_bootstrap():
    data = fetch_fpl_data()
    return jsonify(data)


@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    gw = request.args.get('gameweek', default=1, type=int)
    player_features = get_current_features(gw)  # Implement this
    predictions = predict_points(player_features)
    return jsonify(predictions.tolist())


@app.route('/api/optimize-squad', methods=['POST'])
def optimize_squad_route():
    data = request.json
    predictions_df = pd.DataFrame(data['predictions'])
    selected = optimize_squad(predictions_df)
    return jsonify(selected)


if __name__ == '__main__':
    app.run(debug=True)
