from flask import Flask, request, jsonify, render_template, session
import pandas as pd
import joblib
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure random key

# Load the pre-trained bot model
bot_model = joblib.load('bot_model.pkl')

def initialize_game_state():
    """Initialize a new game state."""
    return {
        'game_round': 0,
        'player_last_sound': None,
        'player_velocity': None,
        'player_acceleration': None,
        'bob_last_sound': None,
        'bob_velocity': None,
        'bob_acceleration': None,
        'bob_win_streak': 0,
        'bob_loss_streak': 0,
        'prev_player_last_sound': None,
        'prev_player_velocity': None,
        'prev_bob_last_sound': None,
        'prev_bob_velocity': None,
        'bob_wins': 0,
        'player_wins': 0,
    }

def get_game_state():
    """Retrieve or initialize the game state for the current session."""
    if 'game_state' not in session:
        session['game_state'] = initialize_game_state()
    return session['game_state']

def save_game_state(state):
    """Save the updated game state to the session."""
    session['game_state'] = state

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/play_round', methods=['POST'])
def play_round():
    game_state = get_game_state()

    data = request.json
    player_reaction_time = data.get('reaction_time', float('inf'))  # Default to inf if not provided
    bob_reaction_time = max(0, np.random.normal(250, 60))  # Ensures Bob's reaction time is not negative

    # Increment the round count
    game_state['game_round'] += 1

    player_won = player_reaction_time < bob_reaction_time

    if player_won:
        # Update Player's stats
        game_state['player_wins'] += 1
        game_state['bob_loss_streak'] += 1
        game_state['bob_win_streak'] = 0

        save_game_state(game_state)
        return jsonify({'waiting_for_blast': True})

    else:
        # Update Bob's stats
        game_state['bob_wins'] += 1
        game_state['bob_win_streak'] += 1
        game_state['bob_loss_streak'] = 0

        # Prepare Bob's inputs
        if game_state['bob_win_streak'] >= 2:
            game_state['bob_velocity'] = game_state['bob_last_sound'] - (game_state['prev_bob_last_sound'] or 0)
        else:
            game_state['bob_velocity'] = None

        if game_state['bob_win_streak'] >= 3:
            game_state['bob_acceleration'] = game_state['bob_velocity'] - (game_state['prev_bob_velocity'] or 0)
        else:
            game_state['bob_acceleration'] = None

        game_state['prev_bob_last_sound'] = game_state['bob_last_sound']
        game_state['prev_bob_velocity'] = game_state['bob_velocity']

        # Predict Bob's blast level
        input_data = pd.DataFrame([[
            game_state['bob_velocity'] or 0,
            game_state['bob_acceleration'] or 0,
            game_state['bob_win_streak'],
            game_state['bob_loss_streak'],
            game_state['player_last_sound'] or 0,
            game_state['player_velocity'] or 0,
            game_state['player_acceleration'] or 0
        ]], columns=[
            'velocity', 'acceleration', 'win_streak', 'loss_streak',
            'opponent_last_sound', 'opponent_velocity', 'opponent_acceleration'
        ])
        bob_blast = int(bot_model.predict(input_data)[0])

        # Update Bob’s last sound
        game_state['prev_bob_last_sound'] = game_state['bob_last_sound']
        game_state['bob_last_sound'] = bob_blast

        save_game_state(game_state)
        return jsonify({'waiting_for_blast': False, 'bob_blast': bob_blast})

@app.route('/set_player_blast', methods=['POST'])
def set_player_blast():
    game_state = get_game_state()

    data = request.json
    player_blast = int(data.get('player_blast', game_state['player_last_sound'] or 0))
    game_state['prev_player_last_sound'] = game_state['player_last_sound']
    game_state['player_last_sound'] = player_blast

    if game_state['player_wins'] >= 2 and game_state['prev_player_last_sound'] is not None:
        game_state['player_velocity'] = game_state['player_last_sound'] - game_state['prev_player_last_sound']
    else:
        game_state['player_velocity'] = None

    if game_state['player_wins'] >= 3 and game_state['prev_player_velocity'] is not None:
        game_state['player_acceleration'] = game_state['player_velocity'] - game_state['prev_player_velocity']
    else:
        game_state['player_acceleration'] = None

    game_state['prev_player_velocity'] = game_state['player_velocity']

    save_game_state(game_state)
    return ('', 204)

if __name__ == '__main__':
    app.run(debug=True)
