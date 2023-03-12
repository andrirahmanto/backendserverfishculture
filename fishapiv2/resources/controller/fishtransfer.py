import os
from flask import Flask, Response, request, current_app, url_for, send_from_directory
from fishapiv2.database.models import *
from flask_restful import Resource
from werkzeug.utils import secure_filename
from fishapiv2.resources.helper import *
import datetime
import json


class FishTransfersApi(Resource):
    def get(self):
        try:
            pipeline = [
                {'$lookup': {
                    'from': 'pond',
                    'let': {"pondid": "$origin_pond_id"},
                    'pipeline': [
                        {'$match': {
                            '$expr': {'$eq': ['$_id', '$$pondid']}}},
                        {"$project": {
                            "created_at": 0,
                            "updated_at": 0,
                        }}
                    ],
                    'as': 'origin_pond'
                }},
                {'$lookup': {
                    'from': 'pond',
                    'let': {"pondid": "$destination_pond_id"},
                    'pipeline': [
                        {'$match': {
                            '$expr': {'$eq': ['$_id', '$$pondid']}}},
                        {"$project": {
                            "created_at": 0,
                            "updated_at": 0,
                        }}
                    ],
                    'as': 'destination_pond'
                }},
                {"$addFields": {
                    "origin_pond": {"$first": "$origin_pond"},
                    "destination_pond": {"$first": "$destination_pond"},
                }},
                {'$lookup': {
                    'from': 'fish_log',
                    'let': {"fish_transfer_id": "$_id"},
                    'pipeline': [
                        {'$match': {
                            '$expr': {'$and': [
                                {'$eq': ['$fish_transfer_id',
                                         '$$fish_transfer_id']},
                                {'$eq': ['$type_log',
                                         'transfer_out']},
                            ]}
                        }},
                        {"$project": {
                            "created_at": 0,
                            "updated_at": 0,
                        }}
                    ],
                    'as': 'fish'
                }},
                {"$project": {
                    "updated_at": 0,
                    "created_at": 0,
                }}

            ]
            fishtransfers = FishTransfer.objects.aggregate(pipeline)
            fishtransfers = list(fishtransfers)
            response = json.dumps(fishtransfers, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def post(self):
        try:
            origin_pond_id = request.form.get("origin_pond_id", None)
            origin_pond = Pond.objects.get(id=origin_pond_id)
            if origin_pond.isActive == False:
                response = {"message": "status pond is not active"}
                response = json.dumps(response, default=str)
                return Response(response, mimetype="application/json", status=400)
            origin_activation = PondActivation.objects(
                pond_id=origin_pond_id, isFinish=False).order_by('-activated_at').first()
            destination_pond_id = request.form.get("destination_pond_id", None)
            destination_pond = Pond.objects.get(id=destination_pond_id)
            fishes_stock = request.form.get("fish_stock", "[]")
            fishes_stock = json.loads(fishes_stock)
            if destination_pond.isActive == False:
                pipeline_year = {'$match': {'$expr': {'$and': [
                    {'$eq': ['$destination_pond_id', {'$toObjectId': destination_pond_id}]},
                    {'$eq': [{'$dateToString': {
                        'format': "%Y", 'date': "$created_at"}}, getYearToday()]},
                ]
                }}}
                list_pond_year = PondActivation.objects.aggregate(pipeline_year)
                list_pond_year = list(list_pond_year)
                id_int = len(list_pond_year) + 1
                water_level = request.form.get("water_level", None)
                activated_at = request.form.get(
                    "activated_at", datetime.datetime.now())
                pond_activation_data = {
                    "id_int": id_int,
                    "pond_id": destination_pond_id,
                    "isFinish": False,
                    "isWaterPreparation": False,
                    "water_level": water_level,
                    "activated_at": activated_at
                }
                destinationPondActivation = PondActivation(**pond_activation_data).save()
                destination_activations = destinationPondActivation.id
                destination_activation_id = destination_activations
                for fish in fishes_stock:
                    # save fish log
                    data_stock = {
                        "pond_id": destination_pond_id,
                        "pond_activation_id": destination_activation_id,
                        "type_log": "activation",
                        "fish_type": fish['type'],
                        "fish_amount": fish['amount'],
                        "fish_total_weight": fish['weight']
                    }
                    # total_fish_harvested += fish['amount']
                    # total_weight_harvested += fish['weight']
                fishlog = FishLog(**data_stock).save()
                destination_pond.update(**{"isActive": True,
        "status": "Aktif",  "pondDoDesc": "Belum Diukur", "pondPhDesc": "Belum Diukur", "pondPh": None, "pondDo": None, "pondTemp": None})
            # fish_grading_id = request.form.get("fish_grading_id", None)
            destination_activation = PondActivation.objects(
                pond_id=destination_pond_id, isFinish=False).order_by('-activated_at').first()
            destination_activation_id = destination_activation.id
            transfer_type = request.form.get("transfer_type", None)
            transfer_method = request.form.get("transfer_method", None)
            sample_weight = request.form.get("sample_weight", None)
            sample_long = request.form.get("sample_long", None)
            fishes = request.form.get("fish", "[]")
            fishes_harvested = request.form.get("fish_harvested", "[]")
            fishes_harvested = json.loads(fishes_harvested)
            fishes = json.loads(fishes)
            if len(fishes) < 1:
                response = {"message": "There is no fish"}
                response = json.dumps(response, default=str)
                return Response(response, mimetype="application/json", status=400)
            # if transfer method is "kering" deactived pond
            if transfer_method == "kering":
                for fish in fishes_harvested:
                # save fish log
                    data = {
                        "pond_id": origin_pond_id,
                        "pond_activation_id": origin_activation.id,
                        "type_log": "deactivation",
                        "fish_type": fish['type'],
                        "fish_amount": fish['amount'],
                        "fish_total_weight": fish['weight']
                    }
                    # total_fish_harvested += fish['amount']
                    # total_weight_harvested += fish['weight']
                fishlog = FishLog(**data).save()
                pond_deactivation_data = {
                    "isFinish": True,
                    "total_fish_harvested": request.form.get("total_fish_harvested", None),
                    "total_weight_harvested": request.form.get("total_weight_harvested", None),
                    "deactivated_at": request.form.get("deactivated_at", datetime.datetime.now()),
                    "deactivated_description": "sortir kering"
                }
                origin_activation.update(**pond_deactivation_data)
                origin_pond.update(**{"isActive": False,"status": "Panen"})
            # update fish grading [optional]
            # if fish_grading_id and transfer_method != "kering":
            #     # pengecekan fish_grading
            #     fish_grading = FishGrading.objects.get(id=fish_grading_id)
            #     # update fishgrading
            #     if transfer_type == "oversized_transfer":
            #         fish_grading.update(**{"isOversizeTransferred": True})
            #     else:
            #         fish_grading.update(**{"isUndersizeTransferred": True})
            # save data
            transfer_at = request.form.get(
            "transfer_at", datetime.datetime.now())
            data = {
                "origin_pond_id": origin_pond_id,
                "destination_pond_id": destination_pond_id,
                "origin_activation_id": origin_activation.id,
                "destination_activation_id": destination_activation_id,
                # "fish_grading_id": None if transfer_method == "kering" else fish_grading_id,
                "transfer_type": None if transfer_method == "kering" else transfer_type,
                "transfer_method": transfer_method,
                "transfer_type": transfer_type,
                "sample_weight": sample_weight,
                "sample_long": sample_long,
                "transfer_at": transfer_at
            }
            fish_transfer = FishTransfer(**data).save()
            # transfer out
            for fish in fishes:
                # save fish log
                data = {
                    "pond_id": origin_pond_id,
                    "pond_activation_id": origin_activation.id,
                    "fish_transfer_id": fish_transfer.id,
                    "type_log": "transfer_out",
                    "fish_type": fish['type'],
                    "fish_total_weight": int(fish['weight']) * -1,
                    "fish_amount": int(fish['amount']) * -1
                }
                fishlog = FishLog(**data).save()
            # transfer in
            for fish in fishes:
                # save fish log
                data = {
                    "pond_id": destination_pond_id,
                    "pond_activation_id": destination_activation_id,
                    "fish_transfer_id": fish_transfer.id,
                    "type_log": "transfer_in",
                    "fish_type": fish['type'],
                    "fish_total_weight": int(fish['weight']),
                    "fish_amount": int(fish['amount'])
                }
                fishlog = FishLog(**data).save()
            response = {"message": "success add fishtransfer"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class FishTransferApi(Resource):
    def put(self, id):
        try:
            body = request.form.to_dict(flat=True)
            FishDeath.objects.get(id=id).update(**body)
            response = {"message": "success change data fish death", "id": id}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def delete(self, id):
        try:
            fishtransfer = FishTransfer.objects.get(id=id)
            # delete fish
            fishes = FishLog.objects.aggregate([
                {'$match': {
                    '$expr': {'$eq': ['$fish_transfer_id', {'$toObjectId': id}]}}},
            ])
            for fish in fishes:
                fishlog = FishLog.objects.get(id=fish['_id'])
                fishlog.delete()
            # delete data
            fishtransfer.delete()
            response = {"message": "success delete fishtransfer"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def get(self, id):
        try:
            pipeline = [
                {'$match': {'$expr': {'$eq': ['$_id', {'$toObjectId': id}]}}},
                {'$lookup': {
                    'from': 'pond',
                    'let': {"pondid": "$origin_pond_id"},
                    'pipeline': [
                        {'$match': {
                            '$expr': {'$eq': ['$_id', '$$pondid']}}},
                        {"$project": {
                            "created_at": 0,
                            "updated_at": 0,
                        }}
                    ],
                    'as': 'origin_pond'
                }},
                {'$lookup': {
                    'from': 'pond',
                    'let': {"pondid": "$destination_pond_id"},
                    'pipeline': [
                        {'$match': {
                            '$expr': {'$eq': ['$_id', '$$pondid']}}},
                        {"$project": {
                            "created_at": 0,
                            "updated_at": 0,
                        }}
                    ],
                    'as': 'destination_pond'
                }},
                {"$addFields": {
                    "origin_pond": {"$first": "$origin_pond"},
                    "destination_pond": {"$first": "$destination_pond"},
                }},
                {'$lookup': {
                    'from': 'fish_log',
                    'let': {"fish_transfer_id": "$_id"},
                    'pipeline': [
                        {'$match': {
                            '$expr': {'$and': [
                                {'$eq': ['$fish_transfer_id',
                                         '$$fish_transfer_id']},
                                {'$eq': ['$type_log',
                                         'transfer_out']},
                            ]}
                        }},
                        {"$project": {
                            "created_at": 0,
                            "updated_at": 0,
                        }}
                    ],
                    'as': 'fish'
                }},
                {"$project": {
                    "updated_at": 0,
                    "created_at": 0,
                }}

            ]
            fishtransfers = FishTransfer.objects.aggregate(pipeline)
            fishtransfers = list(fishtransfers)
            fishtransfer = fishtransfers[0]
            response = json.dumps(fishtransfer, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
