#from app import db
from extensions import db

class Anime(db.Model): 
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    genre = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=True)
    episodes = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50))
    coverImage = db.Column(db.String(300))
    anilist_id = db.Column(db.Integer, nullable=False)
