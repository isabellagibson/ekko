# Base libraries
import hashlib
import json
import uuid
import random
import fastapi
import os
from datetime import datetime
from netifaces import interfaces, ifaddresses, AF_INET
import socket
import requests
from urllib.parse import quote
import base64
import time
import math
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Libraries used for various API functions
from fastapi import Body, FastAPI, Header, Path, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from jinja2 import Template
from typing import Any, AnyStr, Optional, Union, List, Dict

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

ALL_IPS = []
for iface in interfaces():
    for x in [inet['addr'] for inet in ifaddresses(iface).setdefault(AF_INET, [{'addr': 'N/A'}]) if inet['addr'] not in ['127.0.0.1', 'N/A']]:
        if x not in ALL_IPS:
            ALL_IPS.append(x)

ALL_IPS.append('192.168.1.2')
CONFIG = {
    'client_id': '',
    'client_secret': ''
}
if os.path.exists('config.json'):
    CONFIG = json.load(open('config.json', 'r'))
ip_addr = 'localhost'
REDIRECT_URI = f'http://{ip_addr}:8000/callback'
SCOPE = ['user-read-private', 'user-read-email', 'user-library-read']
SPOTIPY_CLIENT = None

def check_ip():    
    for ip in ALL_IPS:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((ip, 8000))
        if result == 0:
            print('Port is opened')
        else:
            print('Port is closed', result)
        sock.close()

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
        return templates.TemplateResponse(name='index.html', context={'request': request})
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

@app.get('/token')
def retrieve_spotify_token():
    SPOTIPY_CLIENT = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CONFIG['client_id'], client_secret=CONFIG['client_secret'], redirect_uri=REDIRECT_URI, scope=SCOPE, open_browser=True))
    return {'success': True, 'config': CONFIG, 'token': json.load(open('.cache', 'r'))}

@app.get('/setup', response_class=HTMLResponse)
def setup(request: fastapi.Request, page: str = None):
    if not page:
        return templates.TemplateResponse(name='setup/intro.html', context={'request': request})
    return templates.TemplateResponse(name=f'setup/{page}.html', context={'request': request, 'ip_addr': 'ip_addr', 'redirect_uri': REDIRECT_URI, 'oauth_url': f'https://accounts.spotify.com/authorize?response_type=code&client_id={CONFIG["client_id"]}&scope={" ".join(SCOPE)}&redirect_uri={REDIRECT_URI}&state=ekko'})

@app.get('/test')
def test():
    check_ip()