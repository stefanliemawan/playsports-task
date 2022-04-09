import os
import requests
from flask import Flask, request, send_from_directory, url_for

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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


    @app.route("/videos")
    def searchVideos():
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

        # send_from_directory("xx","/static/search_filter")
        
        search_response = youtube.search().list(
            q="",
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

        return {
            "results": videos
        }

    
    from . import db
    db.init_app(app)


    return app