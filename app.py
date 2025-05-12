from flask import Flask, render_template, request, jsonify
import os
import random
import json

app = Flask(__name__)

IMAGE_FOLDER = 'static/images'
RATING_FILE = 'ratings.json'
HISTORY_FILE = 'history.json'

K = 32  # Elo constant

# Load image files
images = [f for f in os.listdir(IMAGE_FOLDER) if f.endswith(('.jpg', '.jpeg', '.png'))]

# Always reset ratings/history on startup
ratings = {img: 1000 for img in images}
with open(RATING_FILE, 'w') as f:
    json.dump(ratings, f)

history = []
with open(HISTORY_FILE, 'w') as f:
    json.dump(history, f)

@app.route('/')
def index():
    # Create all possible matchups
    all_pairs = [(a, b) for i, a in enumerate(images) for b in images[i+1:]]

    # Filter out previously seen matchups
    unseen_pairs = [pair for pair in all_pairs if pair not in history and pair[::-1] not in history]

    if not unseen_pairs:
        # Reset history when all matchups have been shown
        unseen_pairs = all_pairs
        history.clear()

    # Choose a random new pair
    left, right = random.choice(unseen_pairs)
    return render_template('index.html', left=left, right=right)

@app.route('/vote', methods=['POST'])
def vote():
    data = request.json
    winner = data['winner']
    loser = data['loser']

    # Update Elo rating
    def expected(rA, rB):
        return 1 / (1 + 10 ** ((rB - rA) / 400))

    Ra, Rb = ratings[winner], ratings[loser]
    Ea, Eb = expected(Ra, Rb), expected(Rb, Ra)

    ratings[winner] = round(Ra + K * (1 - Ea), 2)
    ratings[loser] = round(Rb + K * (0 - Eb), 2)

    # Save ratings
    with open(RATING_FILE, 'w') as f:
        json.dump(ratings, f)

    # Save to history
    match = [winner, loser] if winner < loser else [loser, winner]
    history.append(match)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

    return jsonify(success=True)

@app.route('/rankings')
def rankings():
    sorted_ratings = sorted(ratings.items(), key=lambda x: x[1], reverse=True)
    return jsonify(sorted_ratings)

if __name__ == '__main__':
    app.run(debug=True)
