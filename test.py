from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/test', methods=['POST'])
def test_endpoint():
    data = request.json
    print(f"Received data: {data}")
    return jsonify({'message': 'Success', 'received': data})

if __name__ == '__main__':
    app.run(port=5001, debug=True)
