from flask import Flask, render_template, request, session, redirect, url_for
import os, random, json, uuid
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'secret_key'
app.permanent_session_lifetime = timedelta(days=1)

DATA_DIR = 'user_data'
os.makedirs(DATA_DIR, exist_ok=True)

@app.route('/')
def survey():
    session.clear()
    session['user_id'] = str(uuid.uuid4())
    return render_template('survey.html')

@app.route('/submit_survey', methods=['POST'])
def submit_survey():
    session['survey'] = {
        'age': int(request.form['age']),
        'gender': request.form['gender'].lower(),
        'preferred_gender': request.form['preferred_gender'].lower(),
        'race': request.form['race'].strip().lower(),
        'past_relationships': int(request.form['past_relationships']),
        'places_lived': int(request.form['places_lived']),
        'place_type': request.form['place_type'].strip().lower()
    }

    preferred = session['survey']['preferred_gender']
    if preferred == 'other':
        return redirect(url_for('ineligible'))
    
    img_path = f'static/{preferred}'
    all_images = [f for f in os.listdir(img_path) if f.endswith(('.jpg', '.jpeg', '.png'))]

    # Sample 45 unique images: 30 for comparison, 15 for ranking
    if len(all_images) < 45:
        raise ValueError("Not enough images in directory.")

    selected_images = random.sample(all_images, 45)
    comparison_set = selected_images[:30]
    ranking_set = selected_images[30:]

    # Store in session
    session['comparison_set'] = comparison_set
    session['ranking_set'] = ranking_set

    # Create 30 random pairs from comparison_set
    comparison_pairs = [(comparison_set[i], comparison_set[j])
                        for i in range(len(comparison_set)) for j in range(i+1, len(comparison_set))]
    random.shuffle(comparison_pairs)
    session['pairs'] = comparison_pairs[:30]  # Only keep 30 pairs

    session['votes'] = []
    session['current'] = 0

    return redirect(url_for('compare'))

@app.route('/ineligible')
def ineligible():
    return render_template('ineligible.html')

@app.route('/compare')
def compare():
    idx = session.get('current', 0)
    if idx >= len(session['pairs']):
        return redirect(url_for('rank'))

    left, right = session['pairs'][idx]
    gender = session['survey']['preferred_gender'].lower()
    return render_template('compare.html', left=left, right=right, gender=gender, progress=idx+1)

@app.route('/vote', methods=['POST'])
def vote():
    winner = request.form['winner']
    loser = request.form['loser']
    session['votes'].append({'winner': winner, 'loser': loser})
    session['current'] += 1
    return redirect(url_for('compare'))

@app.route('/rank')
def rank():
    gender = session['survey']['preferred_gender'].lower()
    images = session['ranking_set']
    return render_template('rank.html', images=images, gender=gender)

@app.route('/submit_ranking', methods=['POST'])
def submit_ranking():
    ranking = request.json['ranking']
    user_id = session['user_id']

    data = {
        'user_id': user_id,
        'survey': session['survey'],
        'votes': session['votes'],
        'ranking': ranking
    }

    with open(f'{DATA_DIR}/{user_id}.json', 'w') as f:
        json.dump(data, f)

    return {'status': 'success'}

if __name__ == '__main__':
    app.run(debug=True)
