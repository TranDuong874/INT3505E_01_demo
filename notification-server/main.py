from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook/notify', methods=['POST'])
def webhook_notify():
    data = request.json
    print("[Notification Service] Received webhook:", data)
    return {"status": "received"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
