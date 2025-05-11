from flask import Flask, render_template, request, jsonify
import os
import random
import json

app = Flask(__name__)

IMAGE_FOLDER = 'static/images'
VOTE_FILE = 'votes.json'

# Load image filenames
images = [f for f in os.listdir(IMAGE_FOLDER) if f.endswith(('.jpg', '.jpeg','.png'))]

# Initialize vote data
if not os.path.exists(VOTE_FILE):
    votes = {img: 0 for img in images}
    with open(VOTE_FILE, 'w') as f:
        json.dump(votes, f)
else:
    with open(VOTE_FILE, 'r') as f:
        votes = json.load(f)

@app.route('/')
def index():
    left, right = random.sample(images, 2)
    return render_template('index.html', left=left, right=right)

@app.route('/vote', methods=['POST'])
def vote():
    data = request.json
    winner = data['winner']
    if winner in votes:
        votes[winner] += 1
        with open(VOTE_FILE, 'w') as f:
            json.dump(votes, f)
        return jsonify(success=True)
    return jsonify(success=False), 400

if __name__ == '__main__':
    app.run(debug=True)
