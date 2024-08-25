from flask import Flask, render_template, send_from_directory, abort, jsonify, request, redirect, url_for, flash
import os
import time
import threading
import webbrowser
import json
from datetime import datetime, timezone, timedelta
import random
import keyboard
from humanize import naturalsize
from glob import glob

app = Flask(__name__)
app.secret_key = 'sandcar'

DATA_DIR = 'data'

@app.route('/')
def index():

    folders_data = []
    unlockedFolders = []

    try:
        folders = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
    except FileNotFoundError:
        folders = []

    folders.sort(key=lambda x: int(x), reverse=True)

    for folder in folders:
        if not(os.path.exists(os.path.join(DATA_DIR, folder, '.lock'))):
            unlockedFolders.append(folder)
            activity_path = os.path.join(DATA_DIR, folder, 'activity.json')
            try:
                with open(activity_path, 'r') as file:
                    activity_data = json.load(file)
                    primary = activity_data.get("focused", "N/A")
            except (FileNotFoundError, json.JSONDecodeError):
                primary = "N/A"

            folders_data.append((folder, primary))
        else:
            pass

    try:
        img_folder = random.choice(unlockedFolders)
    except IndexError:
        img_folder = ""
    
    file_size = naturalsize(sum(os.path.getsize(x) for x in glob('./data/**', recursive=True)))
    
    # pages
    per_page = 50
    page = request.args.get('page', 1, type=int)
    total_pages = (len(folders_data) + per_page - 1) // per_page
    folders_data = folders_data[(page - 1) * per_page: page * per_page]

    return render_template(
        'homepage.html',
        folders_data=folders_data,
        img_folder=img_folder,
        capture_amount=len(unlockedFolders),
        currently_capturing=len(folders) - len(unlockedFolders),
        file_size=file_size,
        page=page,
        total_pages=total_pages
    )

@app.route('/connector')
def connector():
    return render_template('connector.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if not query:
        return redirect(url_for('index'))

    results = []
    unlockedFolders = []

    try:
        folders = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
    except FileNotFoundError:
        folders = []

    for folder in folders:
        if not(os.path.exists(os.path.join(DATA_DIR, folder, '.lock'))):
            unlockedFolders.append(folder)
            activity_path = os.path.join(DATA_DIR, folder, 'activity.json')
            try:
                with open(activity_path, 'r') as file:
                    activity_data = json.load(file)
                    text = activity_data.get("text", "")
                    if query.lower() in text.lower():
                        primary = activity_data.get("focused", "N/A")
                        results.append((folder, primary))
            except (FileNotFoundError, json.JSONDecodeError):
                continue
        else:
            pass

    try:
        img_folder = random.choice(unlockedFolders)
    except IndexError:
        img_folder = ""
    
    total_results = len(results)

    # pages
    per_page = 50
    page = request.args.get('page', 1, type=int)
    total_pages = (total_results + per_page - 1) // per_page
    results = results[(page - 1) * per_page: page * per_page]

    return render_template(
        'search.html',
        folders_data=results,
        img_folder=img_folder,
        capture_amount=total_results,
        page=page,
        total_pages=total_pages
    )

@app.route('/<folder>/<filename>')
def serve_file(folder, filename):
    folder_path = os.path.join(DATA_DIR, folder)
    if not os.path.isdir(folder_path):
        abort(404)
    return send_from_directory(folder_path, filename)

@app.template_filter('to_datetime')
def to_datetime_filter(unix_timestamp):
    return datetime.fromtimestamp(int(unix_timestamp), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    app.run(debug=True, port=1337, host='0.0.0.0')
