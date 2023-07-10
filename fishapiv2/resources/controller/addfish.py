import os
from flask_restful import Resource, reqparse
from flask import Flask, Response, request, current_app, url_for, send_from_directory
from fishapiv2.database.models import *
from fishapiv2.resources.helper import *
import datetime
import json

def _validationInput(args):
    # pond id validation
    pond_id = args['pond_id']
    if (pond_id == None):
        raise Exception('Pond_id Tidak boleh kosong')
    pond = Pond.objects(id=pond_id).first()
    if (not pond):
        raise Exception('Pond_id Tidak ditemukan')
    if (pond.isActive == False):
        raise Exception('Pond Tidak dalam musim budidaya')
    # pond activation validation
    pond_activation = PondActivation.objects(
                pond_id=pond_id, isFinish=False).order_by('-activated_at').first()
    if (pond_activation == None):
        raise Exception('Pond Activation yang aktif tidak ditemukan')
    # fish validation
    str_fish_list = args['fish']
    fish_list = json.loads(str_fish_list)
    if (len(fish_list)<1):
        raise Exception('list fish harus lebih dari atau sama dengan 1')
    return True

def createFishIn(pond,pond_activation, fish_list, type_log):
    for fish in fish_list:
        # save fish log
        data = {
            "pond_id": pond.id,
            "pond_activation_id": pond_activation.id,
            "type_log": type_log,
            "fish_type": fish['type'],
            "fish_total_weight": int(fish['weight']) if type_log == 'add_fish' else 0,
            "fish_amount": int(fish['amount'])
        }
        fishlog = FishLog(**data).save()
    return

class AddFishApi(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('pond_id', type=str, required=True, location='form')
            parser.add_argument('fish', type=str, required=True, location='form')
            args = parser.parse_args()
            print(args)
            isValidation = _validationInput(args)
            # get pond
            pond = Pond.objects(id=args['pond_id']).first()
            # get last activation pond
            pond_activation = PondActivation.objects(
                pond_id=pond.id, isFinish=False).order_by('-activated_at').first()
            # get fish list
            str_fish_list = args['fish']
            fish_list = json.loads(str_fish_list)
            # create fish in
            createFishIn(pond,pond_activation,fish_list, 'add_fish')
            response = {"message": "success add fish"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

class EditFishApi(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('pond_id', type=str, required=True, location='form')
            parser.add_argument('fish', type=str, required=True, location='form')
            args = parser.parse_args()
            print(args)
            isValidation = _validationInput(args)
            # get pond
            pond = Pond.objects(id=args['pond_id']).first()
            # get last activation pond
            pond_activation = PondActivation.objects(
                pond_id=pond.id, isFinish=False).order_by('-activated_at').first()
            # get fish list
            str_fish_list = args['fish']
            fish_list = json.loads(str_fish_list)
            # create fish in
            createFishIn(pond,pond_activation,fish_list, 'edit_fish')
            response = {"message": "success edit fish"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
