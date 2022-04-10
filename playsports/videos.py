import os
from flask import Blueprint, request, jsonify
from . import db

from googleapiclient.discovery import build

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
GCN_CHANNEL_ID = os.environ.get("GCN_CHANNEL_ID")
GMTB_CHANNEL_ID = os.environ.get("GMTB_CHANNEL_ID")

bp = Blueprint("videos",__name__, url_prefix="/videos", static_folder="static", static_url_path="/static")

@bp.route("/", methods=["POST"])
def postVideos():
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    search_filter_path = os.path.join(bp.static_folder, "search_filter")
    
    with open(search_filter_path,"r") as f:
        search_filter = f.read()
        search_filter = search_filter.replace("\n","|")

    search_response = youtube.search().list(
        q=search_filter,
        type="video",
        channelId=GCN_CHANNEL_ID or GMTB_CHANNEL_ID,
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

    for video in videos:
        title = video["title"]
        published_at = video["published_at"]
        db.execute_query("INSERT INTO Videos (title, published_at) VALUES (?,?)", (title, published_at))
    
    db.commit_db()
    db.close_db()

    return "Videos commited to SQLite Database"

@bp.route("/", methods=["GET"])
def getVideos():
    rows = db.execute_query("SELECT * FROM Videos").fetchall()
    db.close_db()

    videos = []

    search_query = request.args.get("q")
    if search_query:
        for row in rows:
            if search_query in row["title"]:
                videos.append([x for x in row[:-1]])
    else:
        for row in rows:
            videos.append([x for x in row])
    
    return jsonify(videos)
    
@bp.route("/<id>", methods=["GET"])
def getVideoByID(id):
    row = db.execute_query("SELECT * FROM Videos WHERE id = (?)", (id)).fetchone()
    db.close_db()

    if row:
        video = [x for x in row]
        return jsonify(video)
    else:
        return f"Video with ID {id} not found"
    
@bp.route("/<id>", methods=["DELETE"])
def deleteVideo(id):
    db.execute_query("DELETE FROM Videos WHERE id = (?)", (id))
    db.commit_db()
    db.close_db()

    return f"Video with ID {id} deleted"