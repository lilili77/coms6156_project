from flask import Flask
from flask import request
import os
import json

# This app is deployed in EC2
# Log group for this instance is at  in CloudWatch
app = Flask(__name__)


# Health check
@app.route('/')
def home():
    return "<p>Docker Flask App: Hello, World!</p>"


@app.route('/cp')
def cp():

    return "<p>CP Docker Flask App: Hello, World!</p>"


if __name__ == "__main__":
    for key, val in os.environ.items():
        print(f"{key}------{val}")
    port = int(os.environ.get('PORT', 80))
    app.run(debug=True, host='0.0.0.0', port=port)