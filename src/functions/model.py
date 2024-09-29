import joblib
import json

def load_model(path):
    model = joblib.load(path)
    return model

def load_feature_columns_from_json(filepath):
    with open(filepath, 'r') as f:
        feature_columns = json.load(f)
    return feature_columns


