from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/health")
def health():
  return jsonify(ok=True)

@app.get("/api/hello")
def hello():
  return jsonify(message = "Hello from Flask backend!")

if __name__ == "__main__":
  app.run(port=5000, debug=True)