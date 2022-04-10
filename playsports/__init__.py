import os
from flask import Flask, jsonify
from . import db

from googleapiclient.discovery import build

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "playsports.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    @app.route("/videos", methods=["GET"])
    def getVideos():
        cursor = db.get_db().cursor()
        rows = cursor.execute("SELECT * FROM videos").fetchall()
        db.close_db()

        videos = []
        for row in rows:
            videos.append([x for x in row])
        
        return jsonify(videos)

    @app.route("/videos", methods=["POST"])
    def postVideos():
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

        search_filter_path = os.path.join(app.static_folder, "search_filter")
        
        with open(search_filter_path,"r") as f:
            search_filter = f.read()
            search_filter = search_filter.replace("\n","|")

        search_response = youtube.search().list(
            q=search_filter,
            type="video",
            part="snippet",
            maxResults=10
        ).execute()
        
        items = search_response["items"]
        
        if not items:
            return "Error: No YouTube results"

        videos = [{
            "title": video["snippet"]["title"],
            "published_at":video["snippet"]["publishedAt"]
        } for video in items]

        cursor = db.get_db().cursor()
        for video in videos:
            title = video["title"]
            published_at = video["published_at"]
            cursor.execute(f"INSERT INTO videos (title, published_at) VALUES (?,?)", (title, published_at))
        
        db.commit_db()
        db.close_db()

        return "Videos commited to SQLite Database"
        
        
    
    db.init_app(app)


    return app