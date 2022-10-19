from flask import Flask
import os
import json
app = Flask(__name__)


@app.route('/dbtest')
def dbtest():
    dbhost = json.loads(os.environ.get('dbsecret',"{}"))
    return f"<p>DB host: {dbhost.get('host','Not Found')}</p>"

@app.route('/')
def home():
    return "<p>Docker Flask App: Hello, World!</p>"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 80))
    app.run(debug=True, host='0.0.0.0', port=port)