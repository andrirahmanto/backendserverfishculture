#! /usr/bin/python3
from app import create_app
import logging
import sys

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/html/fishapi')

application = create_app()
