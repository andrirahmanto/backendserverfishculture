#! /usr/bin/python3
from app import create_app
import logging
import sys

logging.basicConfig(stream=sys.stderr)
application = create_app()
