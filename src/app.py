"""
app.py

Author: Lander Combarro Exposito
Created: 2024/04/12
Last Modified: 2024/04/12

Iris Model Prediction API
-------------------------
This Flask API provides functionality for predicting the species of an Iris flower
based on its sepal and petal measurements. The model is a Logistic Regression 
trained on the Iris dataset.

Endpoints
---------
- GET /api/v1/predict: Predict the Iris flower species based on input features (sepal_length, sepal_width, petal_length, petal_width).
- GET /api/v1/retrain: Re-train the model with a new dataset and update the saved model.
- POST /webhook: Update the model by pulling the latest changes from the GitHub repository (used for deployment).

The API also includes basic error handling for missing or invalid parameters, and ensures that the model is always available for predictions.

Dependencies
------------
- Flask
- pandas
- scikit-learn
- pickle
- subprocess

Note: The model and dataset are stored in the absolute paths defined within the script.
"""

# Libraries
import json
import os
import pickle
import subprocess

import pandas as pd
from flask import Flask, jsonify, request
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from utils.iris_model import load_or_initialize_model, train_model, save_model
from utils.variables import CLASS_MAPPING, DATA_PATH, MODEL_PATH

# Change the current working directory to the directory of this script
os.chdir(os.path.dirname(__file__))

# Create a Flask application instance and enable debug mode for development
app = Flask(__name__)
app.config['DEBUG'] = True

# Function to load or initialize the model
model = load_or_initialize_model()

# Landing page route
@app.route('/', methods=['GET'])
def home():
    # Define the response dictionary with message and available endpoints
    response = {
        'message': 'Welcome to the Iris model prediction API',
        'endpoints': {
            '/api/v1/predict': 'Provides predictions based on input features (GET)',
            '/api/v1/retrain': 'Retrains the model with a new dataset (GET)'
        }
    }
    
    # Return the response as a JSON with proper formatting
    return app.response_class(
        response=json.dumps(response, ensure_ascii=False, indent=4),
        status=200,
        mimetype='application/json'
    )

@app.route('/api/v1/predict', methods=['GET'])
def predict():
    try:
        sepal_length = float(request.args.get('sepal_length'))
        sepal_width = float(request.args.get('sepal_width'))
        petal_length = float(request.args.get('petal_length'))
        petal_width = float(request.args.get('petal_width'))
    except (TypeError, ValueError):
        return jsonify({'error': 'Debe proporcionar todos los parámetros numéricos'}), 400

    prediction = model.predict([[sepal_length, sepal_width, petal_length, petal_width]])
    class_name = CLASS_MAPPING[int(prediction[0])]

    return jsonify({'prediction': class_name})

@app.route('/api/v1/retrain', methods=['GET'])
def retrain():
    if os.path.exists(DATA_PATH):
        model = train_model(data_path=DATA_PATH)
        # accuracy = accuracy_score(y_test, model.predict(X_test))
        save_model(model, model_path=MODEL_PATH)
        # return jsonify({'message': 'Modelo reentrenado', 'accuracy': accuracy})
        return jsonify({'message': 'Modelo reentrenado'})
    else:
        return jsonify({'error': 'No se encontró el dataset para reentrenamiento'}), 404


# # LUIS
# @app.route('/webhook', methods=['POST'])
# def webhook():
#     repo_path = '/home/LuTaOr/Despliegue_API'
#     server_wsgi = '/var/www/lutaor_pythonanywhere_com_wsgi.py'

#     if request.is_json:
#         subprocess.run(['git', '-C', repo_path, 'pull'], check=True)
#         subprocess.run(['touch', server_wsgi], check=True)
#         return jsonify({'message': 'Despliegue actualizado con éxito'}), 200
#     else:
#         return jsonify({'error': 'Solicitud no válida'}), 400





if __name__ == '__main__':
    app.run()

