import json
import threading
import fastapi
import os
from datetime import datetime
from netifaces import interfaces, ifaddresses, AF_INET
import requests
from urllib.parse import quote
import base64
import time
import math
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from fastapi import Body, FastAPI, Header, Path, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from jinja2 import Template
from typing import Any, AnyStr, Optional, Union, List, Dict
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
JSONBody = Union[List[Any], Dict[AnyStr, Any]]

def get_temporary_token(client_id, client_secret, code, redirect_uri):
    req = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri
    }, headers={
        'Authorization': 'Basic ' + base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode(),
        'Content-Type': 'application/x-www-form-urlencoded'
    })
    req = json.loads(req.text)
    req['expires_at'] = math.floor(time.time()) + req['expires_in']
    open('.cache', 'w').write(json.dumps(req, indent=2))
    return req

def read_html(filename):
    return '\n'.join(open(f'templates/{filename}.html', 'r').readlines())

ALL_IPS = []
for iface in interfaces():
    for x in [inet['addr'] for inet in ifaddresses(iface).setdefault(AF_INET, [{'addr': 'N/A'}]) if inet['addr'] not in ['127.0.0.1', 'N/A']]:
        if x not in ALL_IPS:
            ALL_IPS.append(x)

ALL_IPS.append('192.168.1.2')
CONFIG = {
    'client_id': '',
    'client_secret': '',
    'tags': []
}
ip_addr = os.popen('hostname -I').read().strip()
REDIRECT_URI = f'http://{ip_addr}:8000/callback'
SCOPE = ['user-library-read', 'user-modify-playback-state', 'user-read-playback-state', 'user-read-currently-playing', 'user-follow-modify', 'user-follow-read', 'user-read-recently-played', 'user-read-playback-position', 'user-top-read', 'playlist-read-collaborative', 'playlist-modify-public', 'playlist-read-private', 'playlist-modify-private', 'app-remote-control', 'streaming', 'user-read-email', 'user-read-private', 'user-library-modify', 'user-library-read']
SPOTIPY_CLIENT = None
RFID_READER = SimpleMFRC522()
if os.path.exists('config.json'):
    CONFIG = json.load(open('config.json', 'r'))
    SPOTIPY_CLIENT = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CONFIG['client_id'], client_secret=CONFIG['client_secret'], redirect_uri=REDIRECT_URI, scope=SCOPE))
READER_BUSY = False

def read_rfid_tag():
    global RFID_READER
    global READER_BUSY
    tag_id = None
    if READER_BUSY:
        return tag_id
    try:
        tag_id = str(RFID_READER.read()[0])
    finally:
        GPIO.cleanup()
        READER_BUSY = False
    return tag_id

def read_html(filename):
    return '\n'.join(open(f'templates/{filename}.html', 'r').readlines())

app = FastAPI(docs_url=None, redoc_url=None)
app.add_middleware(
    CORSMiddleware, allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'])
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get('/')
def index(request: fastapi.Request):
    if os.path.exists('config.json'):
        return templates.TemplateResponse(name='template.html', context={'request': request, 'page_content': read_html('index'), 'num_tags': len(CONFIG['tags']), 'page_title': 'Home'})
    return RedirectResponse('/setup', 307)

@app.get('/tags')
def index(request: fastapi.Request):
    if os.path.exists('config.json'):
        return templates.TemplateResponse(name='template.html', context={'request': request, 'page_content': read_html('tags'), 'page_title': 'Tags'})
    return RedirectResponse('/setup', 307)

@app.post('/config')
def save_config(body: JSONBody = None):
    global SPOTIPY_CLIENT
    global CONFIG
    data = {}
    if os.path.exists('config.json'):
        data = json.load(open('config.json', 'r'))
    body = jsonable_encoder(body)
    for key in list(body.keys()):
        data[key] = body[key]
    open('config.json', 'w').write(json.dumps(data, indent=2))
    CONFIG = data
    return {'success': True}

@app.get('/callback')
def callback(code: str = None):
    global CONFIG
    global SPOTIPY_CLIENT
    if not code:
        return HTTPException(400)
    x = get_temporary_token(CONFIG['client_id'], CONFIG['client_secret'], code, REDIRECT_URI)
    return x

@app.get('/{item_type}/{item_id}')
def get_information(item_type: str, item_id: str):
    global SPOTIPY_CLIENT
    if item_type == 'album':
        return SPOTIPY_CLIENT.album(item_id)
    elif item_type == 'playlist':
        return SPOTIPY_CLIENT.playlist(item_id)

@app.get('/token')
def retrieve_spotify_token():
    global SPOTIPY_CLIENT
    SPOTIPY_CLIENT = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CONFIG['client_id'], client_secret=CONFIG['client_secret'], redirect_uri=REDIRECT_URI, scope=SCOPE, open_browser=True))
    return {'success': True, 'config': CONFIG, 'token': json.load(open('.cache', 'r'))}

@app.get('/setup', response_class=HTMLResponse)
def setup(request: fastapi.Request, page: str = None):
    if not page:
        return templates.TemplateResponse(name='setup/intro.html', context={'request': request})
    return templates.TemplateResponse(name=f'setup/{page}.html', context={'request': request, 'ip_addr': 'ip_addr', 'redirect_uri': REDIRECT_URI, 'oauth_url': f'https://accounts.spotify.com/authorize?response_type=code&client_id={CONFIG["client_id"]}&scope={" ".join(SCOPE)}&redirect_uri={REDIRECT_URI}&state=ekko'})

@app.get('/read_tag')
def read_tag():
    global READER_BUSY
    READER_BUSY = True
    return {'data': read_rfid_tag()}

@app.post('/tags')
def create_tag(body: JSONBody = None):
    global CONFIG
    if 'tags' not in CONFIG:
        CONFIG['tags'] = []
    body = jsonable_encoder(body)
    CONFIG['tags'].append(body)
    open('config.json', 'w').write(json.dumps(CONFIG, indent=2))
    return {'success': True, 'data': body}

def tag_reading_daemon():
    global READER_BUSY
    global SPOTIPY_CLIENT
    while True:
        tag_id = read_rfid_tag()
        if tag_id:
            uri = [tag['uri'] for tag in CONFIG['tags'] if tag['tag_id'] == tag_id][0]
            print('Detected ' + uri)
            SPOTIPY_CLIENT.start_playback(context_uri=uri)
        time.sleep(10)

threading.Thread(target=tag_reading_daemon).start()