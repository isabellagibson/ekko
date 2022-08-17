# Base libraries
import hashlib
import json
import uuid
import random
import fastapi
import os
from datetime import datetime

# Libraries used for various API functions
from fastapi import Body, FastAPI, Header, Path, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from jinja2 import Template


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

@app.get('/setup', response_class=HTMLResponse)
def setup(request: fastapi.Request, page: str = None):
    if not page:
        return templates.TemplateResponse(name='setup/intro.html', context={'request': request})
    return templates.TemplateResponse(name=f'setup/{page}.html', context={'request': request})