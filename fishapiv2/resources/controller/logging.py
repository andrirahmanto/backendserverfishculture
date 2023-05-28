import os
from flask import Flask, Response, request, jsonify, current_app, url_for, send_from_directory, make_response
from fishapiv2.database.models import *
from flask_restful import Resource
import jwt
from functools import wraps
from werkzeug.utils import secure_filename
from fishapiv2.resources.helper import *
import datetime
import json
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash


class LoggingApi(Resource):
    def get(seft):
        try:
            pipeline_logging = {"$sort": {"start_at": 1}},
            logging = Logging.objects.aggregate(pipeline_logging)
            list_logging = list(logging)
            response = json.dumps(list_logging, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": "gagal post logging"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
    def post(self):
        try:

            feature_name = request.form.get('feature_name', None)
            start_at = datetime.datetime.now
            end_at = datetime.datetime.now
            duration = str(end_at + start_at)
            breeder_name = request.form.get('breeder_name', None)
            farm_name = request.form.get('farm_name', None)
            data_log = {

                "farm_name": farm_name,
                "breeder_name": breeder_name,
                "start_at": start_at,
                "end_at": end_at,
                "duration": duration,
                "feature_name": feature_name,
            }
            logging = Logging(**data_log).save()
            response = {"message": "success add logging"}
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
