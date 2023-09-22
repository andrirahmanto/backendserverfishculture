from flask import Response, request, current_app
from fishapiv2.database.models import FishGrading, Pond, PondActivation, FeedHistory
from flask_restful import Resource, reqparse
import datetime
import json
from fishapiv2.resources.helper import *


class FishGradingsApi(Resource):
    def get(self):
        try:
            pipeline = [
                {'$lookup': {
                    'from': 'pond',
                    'let': {"pondid": "$pond_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$pondid']}}},
                        {"$project": {
                            "_id": 1,
                            "alias": 1,
                            "location": 1,
                            "build_at": 1,
                            "isActive": 1,
                        }}
                    ],
                    'as': 'pond'
                }},
                {'$lookup': {
                    'from': 'pond_activation',
                    'let': {"activationid": "$pond_activation_id"},
                    'pipeline': [
                        {'$match': {
                            '$expr': {'$eq': ['$_id', '$$activationid']}}},
                        {"$project": {
                            "_id": 1,
                            "isFinish": 1,
                            "isWaterPreparation": 1,
                            "water_level": 1,
                            "activated_at": 1
                        }}
                    ],
                    'as': 'pond_activation'
                }},
                {"$addFields": {
                    "pond": {"$first": "$pond"},
                    "pond_activation": {"$first": "$pond_activation"},
                }},
                {"$project": {
                    "updated_at": 0,
                    "created_at": 0,
                }}
            ]
            fishgrading = FishGrading.objects.aggregate(pipeline)
            list_fishgradings = list(fishgrading)
            response = json.dumps(list_fishgradings, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def post(self):
        try:

            def _gradingValidation(args):
                # pond id validation
                if (args['pond_id'] == None):
                    raise Exception('Pond_id Tidak boleh kosong')
                pond = Pond.objects(id=args['pond_id']).first()
                if (not pond):
                    raise Exception('Pond_id Tidak ditemukan')
                if (pond.isActive == False):
                    raise Exception('Pond Tidak dalam keadaan aktif')
                # get last activation
                last_pond_activation = PondActivation.objects(
                pond_id=pond.id, isFinish=False).order_by('-activated_at').first()
                if (not last_pond_activation):
                    raise Exception('Masa budidaya tidak ditemukan')
                return
            
            def _getTotalWeightFromListFishLastGrading(listFish):
                totalWeight = 0
                for fish in listFish:
                    weight = fish['amount']*fish['weight']
                    totalWeight += weight
                return totalWeight

            def _getTotalWeightFromListFishNow(listFish, avg_weight):
                totalWeight = 0
                for fish in listFish:
                    weight = fish['amount'] * avg_weight
                    totalWeight += weight
                return totalWeight

            def _getNewListFish(listFish, avg_weight):
                new_list_fish = []
                for fish in listFish:
                    fish['weight'] = avg_weight
                    new_list_fish.append(fish)
                return new_list_fish

            parser = reqparse.RequestParser()
            parser.add_argument('pond_id', type=str, required=True, location='form')
            parser.add_argument('avg_weight', type=float, required=True, location='form')
            parser.add_argument('sample_amount', type=int, default=0, location='form')
            parser.add_argument('sample_weight', type=float, default=0, location='form')
            parser.add_argument('sample_long', type=float, default=0, location='form')
            args = parser.parse_args()
            validation = _gradingValidation(args=args)
            pond = Pond.objects(id=args['pond_id']).first()
            last_pond_activation = PondActivation.objects(pond_id=pond.id, isFinish=False).order_by('-activated_at').first()
            last_grading_activation = FishGrading.objects(pond_activation_id=last_pond_activation.id).order_by('-grading_at').first()
            date_last_grading_activation = last_grading_activation.grading_at
            date_now = datetime.datetime.now()
            total_feed_dose_before_last_grading = FeedHistory.objects(
                pond_activation_id=last_pond_activation.id,
                feed_history_time__lt=date_last_grading_activation
            ).sum('feed_dose')
            total_feed_dose_before_now = FeedHistory.objects(
                pond_activation_id=last_pond_activation.id,
                feed_history_time__lt=date_now
            ).sum('feed_dose')
            diff_feed_dose = total_feed_dose_before_now-total_feed_dose_before_last_grading
            total_fish_weight_last_grading = _getTotalWeightFromListFishLastGrading(list(last_grading_activation.fish))
            total_fish_weight_now = _getTotalWeightFromListFishNow(list(last_grading_activation.fish), args['avg_weight'])
            diff_fish_weight = total_fish_weight_now - total_fish_weight_last_grading
            fcr = diff_feed_dose / diff_fish_weight
            fishGradingNew = FishGrading(
                pond_id = pond.id,
                pond_activation_id = last_pond_activation.id,
                event_desc = 'GRADING',
                fish = _getNewListFish(list(last_grading_activation.fish), args['avg_weight']),
                fcr = fcr,
                sample_amount = args['sample_amount'],
                sample_weight = args['sample_weight'],
                sample_long = args['sample_long'],
            )
            fishGradingNew.save(using=current_app.config['CONNECTION'])

            response = {"message": "Berhasil add grading"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class FishGradingApi(Resource):
    def put(self, id):
        try:
            body = request.form.to_dict(flat=True)
            FishGrading.objects.get(id=id).update(**body)
            response = {
                "message": "success change data fish grading", "id": id}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)

    def delete(self, id):
        try:
            fishgrading = FishGrading.objects.get(id=id).delete(using=current_app.config['CONNECTION'])
            response = {"message": "success delete fish grading"}
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
                    'let': {"pondid": "$pond_id"},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$_id', '$$pondid']}}},
                        {"$project": {
                            "_id": 1,
                            "alias": 1,
                            "location": 1,
                            "build_at": 1,
                            "isActive": 1,
                        }}
                    ],
                    'as': 'pond'
                }},
                {'$lookup': {
                    'from': 'pond_activation',
                    'let': {"activationid": "$pond_activation_id"},
                    'pipeline': [
                        {'$match': {
                            '$expr': {'$eq': ['$_id', '$$activationid']}}},
                        {"$project": {
                            "_id": 1,
                            "isFinish": 1,
                            "isWaterPreparation": 1,
                            "water_level": 1,
                            "activated_at": 1
                        }}
                    ],
                    'as': 'pond_activation'
                }},
                {"$addFields": {
                    "pond": {"$first": "$pond"},
                    "pond_activation": {"$first": "$pond_activation"},
                }},
                {"$project": {
                    "updated_at": 0,
                    "created_at": 0,
                }}
            ]
            fishgrading = FishGrading.objects.aggregate(pipeline)
            list_fishgradings = list(fishgrading)
            response = json.dumps(list_fishgradings[0], default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)


class FishGradingGraphApi(Resource):
    def get(self, activationOrPondId):

        def _getTotalWeightFromListFishLastGrading(listFish):
                totalWeight = 0
                for fish in listFish:
                    weight = fish['amount']*fish['weight']
                    totalWeight += weight
                return totalWeight

        def _getActivationByActivationOrPondId(activationOrPondId):
            # pond id and pond activation id cant be null at the same time
            if (activationOrPondId == None or activationOrPondId==''):
                raise Exception('id tidak boleh kosong')
            pond_activation = PondActivation.objects(id=activationOrPondId).first()
            if (pond_activation):
                return pond_activation
            pond = Pond.objects(id=activationOrPondId).first()
            if (pond):
                last_pond_activation = PondActivation.objects(
                pond_id=pond.id, isFinish=False).order_by('-activated_at').first()
                return last_pond_activation
            raise Exception('activationOrPondId tidak valid')
            return
        print(activationOrPondId)
        list_fish_weight = []
        list_fish_feed_history = []
        pond_activation = _getActivationByActivationOrPondId(activationOrPondId)
        # get date activation
        date_activation = pond_activation.activated_at.replace(hour=23, minute=59, second=59)
        date_before_activation = date_activation - timedelta(days=1)
        list_fish_weight.append({'date' : date_before_activation,'total_weight_fish' : 0,})
        list_fish_feed_history.append({'date' : date_before_activation,'total_feed_dose' : 0,})
        # get date now
        date_now = datetime.datetime.now().replace(hour=23, minute=59, second=59)
        # get day beetween date
        day_beetween_date = getListDateBettwenDate(dateA=date_activation, dateB=date_now)
        # get fish weight per day
        for day in day_beetween_date:
            item_fish = {
                'date' : datetime.datetime.now(),
                'total_weight_fish' : 0,
            }
            item_feed = {
                'date' : datetime.datetime.now(),
                'total_feed_dose' : 0,
            }
            fish_grading = FishGrading.objects(
                pond_activation_id=pond_activation.id,
                grading_at__lt=day,
            ).order_by('-grading_at').first()
            total_weight_fish = _getTotalWeightFromListFishLastGrading(fish_grading.fish)
            item_fish['date'] = day
            item_fish['total_weight_fish'] = total_weight_fish
            list_feed_dose = FeedHistory.objects(
                pond_activation_id=pond_activation.id,
                feed_history_time__lt=day,
            )
            total_feed_dose = list_feed_dose.sum('feed_dose')
            item_feed['date'] = day
            item_feed['total_feed_dose'] = total_feed_dose
            list_fish_weight.append(item_fish)
            list_fish_feed_history.append(item_feed)

        response = {
            "list_fish_weight": list_fish_weight,
            "list_fish_feed_history": list_fish_feed_history,
        }
        response = json.dumps(response, default=str)
        return Response(response, mimetype="application/json", status=200)


class FishGradingApiByActivation(Resource):
    def get(self, activation_id):
        try:
            pipeline = [
                {'$match': {
                    '$expr': {'$eq': ['$pond_activation_id', {'$toObjectId': activation_id}]}}},
                {"$sort": {"grading_at": -1}}
            ]
            fishgrading = FishGrading.objects.aggregate(pipeline)
            list_fishgradings = list(fishgrading)
            response = json.dumps(list_fishgradings, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)
