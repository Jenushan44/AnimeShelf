from flask import Flask
from flask import request, abort 
from flask import jsonify 
from flask_cors import CORS
from models import Anime 
from extensions import db
from sqlalchemy.exc import IntegrityError

import requests

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///animes.db'

db.init_app(app) 

@app.route('/')
def home():
    return "AnimeShelf running"

@app.route('/list', methods=['GET'])
def get_list():
    # Fetches data from the database 
    show_list = Anime.query.all()
    result = []
    for item in show_list: 
        result.append({
            'id': item.id, 
            'title': item.title, 
            'genre': item.genre, 
            'score': item.score,
            'status': item.status,
            'coverImage': item.coverImage,
            'anilist_id': item.anilist_id
        })
    return jsonify(result), 200

@app.route('/list', methods=['POST'])
def add_list():
    # Gets JSON data from body of incoming HTTP request to store in data variable 
    data = request.get_json()
    new_item = Anime(
        title=data['title'],
        genre=data['genre'],
        score=data['score'],
        status=data.get("status", "Watching"),
        episodes=data["episodes"],
        coverImage=data["coverImage"],
        anilist_id=data["anilist_id"]

    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({'message': 'Anime entry added'}), 201 

@app.route('/list/<int:show_id>', methods=['DELETE'])
def delete_list(show_id):
    item = Anime.query.get(show_id) # Find anime entry in database with id 
    if not item:
        abort(404, description="Anime not found") 
    db.session.delete(item) # deletes show entry with same anime id
    db.session.commit() # commit changes to database 
    return jsonify({'message': 'Anime deleted'}), 200

@app.route('/media', methods=['POST'])
def save_media():
    data = request.get_json()
    print("Success", data)

    new_item = Anime(
        title=data["title"],
        genre=data["genre"],
        score=data["score"],
        status=data.get("status", "Watching"),
        episodes=data["episodes"],
        coverImage=data["coverImage"],
        anilist_id=data["anilist_id"],


    )

    try:         
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'message': 'saved'}), 201
    except IntegrityError: #Error when breaking database rules
        db.session.rollback() # Changes back to state before adding show
        return jsonify({'message': 'Anime already in list'}), 400 


@app.route('/list/<int:show_id>', methods=['PUT'])
def update_score(show_id): 
    item = Anime.query.get(show_id)
    if not item:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json()
    new_score = data.get("score")
    new_status = data.get("status")
    item.score = new_score
    item.status = new_status 

    db.session.commit()
    return jsonify({'message': 'saved'}), 200

@app.route('/profile', methods=['GET'])
def view_profile(): 
    show_list = Anime.query.all()
    time_watched = 0
    episodes_watched = 0
    for show in show_list: 
        time_watched += show.episodes * 24
        episodes_watched += show.episodes
    total_days = round(time_watched/1440, 2)
    
    return jsonify({
        "total": total_days, # becomes data.total in React with total being the key
        "episodes": episodes_watched # becomes data.episodes in React with episodes being the key
        }), 200

@app.route('/search', methods=['GET'])
def show_anime():
    title = request.args.get('title')
    
    
    query = f"""
    {{
        Media(search: "{title}") {{
        title {{ english }}
        episodes
        format 
        coverImage {{ large }} 
        }}
    }}
    """
    # coverImage

    mydict = {"query": query}
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        "https://graphql.anilist.co",
        json=mydict,
        headers=headers
    )

    data = response.json()
    return jsonify(data), 200
 

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
