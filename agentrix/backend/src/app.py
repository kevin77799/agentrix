from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the AgentriX backend!"})

@app.route('/api/data', methods=['GET'])
def get_data():
    # Example data retrieval logic
    data = {"key": "value"}
    return jsonify(data)

@app.route('/api/data', methods=['POST'])
def post_data():
    new_data = request.json
    # Example logic to handle incoming data
    return jsonify({"received": new_data}), 201

if __name__ == '__main__':
    app.run(debug=True)