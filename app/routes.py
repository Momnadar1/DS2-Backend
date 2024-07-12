from app import app
from flask import render_template, jsonify, request
import os
import pandas as pd
import json

DATASETS_DIR = 'datasets'
FEATURE_COLUMNS_FILE = 'saved_features_columns.json'
datasets = []

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html', title='Hello from Momna', message='Hello Users, Welcome!!')

@app.route('/datasets', methods=['GET'])
def list_datasets():
    global datasets
    datasets = [f for f in os.listdir(DATASETS_DIR) if f.endswith('.csv')]
    # for f in os.listdir(DATASETS_DIR):
    #     if f.endswith('.csv'):
    #         datasets.append(f)
    return jsonify(datasets)

@app.route('/datasets', methods=['POST'])
def post_dataset():
    dataset_name = request.form
    if dataset_name.get('dataset_name'):
        dataset_name = dataset_name['dataset_name'] 
        dataset_path = os.path.join(DATASETS_DIR, dataset_name)
    
        if os.path.exists(dataset_path):
            df = pd.read_csv(dataset_path)
            first_10_rows = df.head(10).to_json(orient='records')
            return jsonify({'data': first_10_rows})
        else:
            return jsonify({'error': 'Dataset not found'}), 404
    else:
        return jsonify({'error': 'Request Body: Internal server error'}), 500

def load_feature_columns():
    if os.path.exists(FEATURE_COLUMNS_FILE):
        with open(FEATURE_COLUMNS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_feature_columns(columns):
        with open(FEATURE_COLUMNS_FILE, 'w') as file:
            json.dump(columns, file)

@app.route('/features', methods=['POST'])
def save_columns():
    data = request.json
    selected_columns = data.get('selected', [])
    
    print("Selected columns:", selected_columns)

    save_feature_columns(selected_columns)
    
    return jsonify({"success": True, "features": selected_columns})


@app.route('/features', methods=['GET'])
def get_features():
    feature_columns = load_feature_columns()
    return jsonify({"features": feature_columns})

@app.route('/target_columns', methods=['POST'])
def get_unselected_columns():
    dataset_name = request.form
    print(dataset_name)
    if dataset_name.get('dataset_name'):
        dataset_name = dataset_name['dataset_name']
        dataset_path = os.path.join(DATASETS_DIR, dataset_name)
    
        if os.path.exists(dataset_path) and dataset_name:
            
            df = pd.read_csv(dataset_path)
            all_columns = set(df.columns)
            selected_columns = set(load_feature_columns())
            unselected_columns = list(all_columns - selected_columns)
            print("Unselected columns:", unselected_columns)
            return jsonify({'unselected_columns': unselected_columns})
        else:
            return jsonify({'error': 'Dataset not found'}), 404
    else:
        return jsonify({'error': 'Request Body: Internal server error'}), 500
