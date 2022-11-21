import os
from flask import Flask, Response, request, current_app, url_for, send_from_directory
from fishapi.database.models import *
from flask_restful import Resource
from werkzeug.utils import secure_filename
from fishapi.resources.helper import *
import datetime
import json


class StatisticApi(Resource):
    def get(self):
        # try:
        # total pond
        total_pond = len(Pond.objects())
        # active pond
        active_pond = Pond.objects(isActive=True)
        active_culture_season = PondActivation.objects(isFinish=False)
        id_active_culture_season = []
        for obj in active_culture_season:
            id_active_culture_season.append(obj.id)
        print(id_active_culture_season)
        total_active_pond = len(active_pond)

        # fish live
        total_fish_live = FishLog.objects(
            pond_activation_id__in=id_active_culture_season).sum("fish_amount")

        # fish death
        total_fish_death = FishLog.objects(
            pond_activation_id__in=id_active_culture_season, type_log="death").sum("fish_amount") * -1

        # fish harvested
        close_culture_season = PondActivation.objects(isFinish=True)
        total_fish_harvested = close_culture_season.sum(
            "total_weight_harvested")

        # feed dose
        feed_dose = FeedHistory.objects(
            pond_activation_id__in=id_active_culture_season)
        total_feed_dose = feed_dose.sum("feed_dose")

        # fish weight
        fish_weight = [
            {"type": "nila hitam",
             "amount": 0},
            {"type": "nila merah",
             "amount": 0},
            {"type": "lele",
             "amount": 0},
            {"type": "patin",
             "amount": 0},
            {"type": "mas",
             "amount": 0},
        ]
        for i in range(len(fish_weight)):
            # get last check
            print(fish_weight[i]["type"])
            last_check = FishGrading.objects(
                pond_activation_id__in=id_active_culture_season, fish_type=fish_weight[i]["type"]).order_by(
                "-created_at").first()
            print(last_check)
            if last_check:
                fish_weight[i]["amount"] = last_check.avg_fish_weight
        # water quality
        normal_ph = 0
        normal_do = 0
        normal_floc = 0
        for culture_season in active_culture_season:
            # get last daily water quality
            last_daily_water_quality = DailyWaterQuality.objects(
                pond_activation_id=culture_season.id).order_by("-created_at").first()
            if not last_daily_water_quality:
                continue
            ph = last_daily_water_quality.ph
            do = last_daily_water_quality.do
            if ph > 6 and ph < 8:
                normal_ph += 1
            if do > 4 and do < 6:
                normal_do += 1
            # get last weekly water quality
            last_weekly_water_quality = WeeklyWaterQuality.objects(
                pond_activation_id=culture_season.id).order_by("-created_at").first()
            if not last_weekly_water_quality:
                continue
            floc = last_weekly_water_quality.floc
            if floc == "11-30":
                normal_floc += 1
        abnormal_ph = len(active_culture_season) - normal_ph
        abnormal_do = len(active_culture_season) - normal_do
        abnormal_floc = len(active_culture_season) - normal_floc

        response = {
            "total_pond": total_pond,
            "active_pond": total_active_pond,
            "fish_live": total_fish_live,
            "fish_death": total_fish_death,
            "fish_harvested": total_fish_harvested,
            "total_feed_dose": total_feed_dose,
            "fishes_weight": fish_weight,
            "water_quality": {
                "ph": {
                    "normal": normal_ph,
                    "abnormal": abnormal_ph
                },
                "do": {
                    "normal": normal_do,
                    "abnormal": abnormal_do
                },
                "floc": {
                    "normal": normal_floc,
                    "abnormal": abnormal_floc
                }
            }
        }
        response = json.dumps(response, default=str)
        return Response(response, mimetype="application/json", status=200)
        # except Exception as e:
        #     response = {"message": str(e)}
        #     response = json.dumps(response, default=str)
        #     return Response(response, mimetype="application/json", status=400)
