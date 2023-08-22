from flask import *
from flask_restful import Resource, reqparse
from fishapiv2.database.models import *
from fishapiv2.resources.helper import *
import datetime
import json

inpt_json_transfer_basah = {
    'origin_pond_id': 'obid(1288374682374)',
    'fish_sort_type' : 'basah',
    'transfer_list' : [
        {
            'destination_pond_id':'obid(64310c3ae3eba0b2824fecd5)',
            'status': 'isActivated',
            'fish': [
                {"type": "lele","amount": 5, "weight":1},
                {"type": "nila merah","amount": 9, "weight":1}
            ],
            'sample_weight': 20,
            'sample_long': 20,
            'transfer_type': 'oversized_transfer'
        },
        {
            'destination_pond_id':'obid(1288374682374)',
            'status': 'isActivated',
            'fish': [
                {"type": "lele","amount": 5, "weight":23},
                {"type": "patin","amount": 9, "weight":23}
            ],
            'sample_weight': 20,
            'sample_long': 20,
            'transfer_type': 'undersized_transfer'
        },
        
    ] 
}

# NOTE: ikan di kolam harus habis, dan bisa transfer ikan ke kolam yang belum di aktivasi
inpt_json_transfer_kering = {
    'origin_pond_id': '64a2f873b8354d11ab456639',
    'fish_sort_type' : 'kering',
    'amount_undersize' : 5,
    'amount_oversize' : 4,
    'amount_normal' : 5,
    'sample_weight' : 10,
    'sample_amount' : 3,
    'sample_long' : 30,
    'total_fish_harvested' : 14,
    'total_weight_harvested' : 20,
    'transfer_list' : [
        {
            'destination_pond_id':'64a2f857b8354d11ab456638',
            'status': 'isActivated',
            'fish': [
                {"type": "nila merah","amount": 5, "weight":12},
                {"type": "lele","amount": 3, "weight":12}
            ],
            'sample_weight': 20,
            'sample_long': 20,
            'transfer_type': 'oversized_transfer'
        },
        {
            'destination_pond_id':'64a2f88fb8354d11ab45663a',
            'status': 'isActivated',
            'fish': [
                {"type": "lele","amount": 4, "weight":23},
                {"type": "patin","amount": 3, "weight":23}
            ],
            'sample_weight': 20,
            'sample_long': 20,
            'transfer_type': 'undersized_transfer'
        },
    ],
    'fish_death': [
        {"type": "lele","amount": 5},
        {"type": "patin","amount": 9}
    ]
}

def _transferListValidation(i,transfer):
    # destination pond id
    destination_pond_id = transfer['destination_pond_id']
    if (destination_pond_id == None):
        raise Exception('Pond_id pada transfer_list ke %s tidak boleh kosong' % (i))
    pond = Pond.objects(id=destination_pond_id).first()
    if (not pond):
        raise Exception('destination_pond_id pada transfer_list ke %s harus memiliki status' % (i))
    # status
    if (transfer['status']!='isActivated' and transfer['status']!='isNotActivated'):
        raise Exception('destination_pond_id pada transfer_list ke %s harus memiliki status' % (i))
    # fish
    if (len(transfer['fish'])< 1):
        raise Exception('transfer_list ke %s harus memiliki setidaknya 1 jenis ikan yang akan dipindahkan' % (i))
    # sample weight
    if (transfer['sample_weight']==None or transfer['sample_weight']<1):
        raise Exception('transfer_list ke %s harus memiliki sample weight' % (i))
    # sample long
    if (transfer['sample_long']==None or transfer['sample_long']<1):
        raise Exception('transfer_list ke %s harus memiliki sample long' % (i))
    if (transfer['transfer_type'] != "oversized_transfer" and transfer['transfer_type'] != "undersized_transfer" and transfer['transfer_type'] != "maintain_transfer"):
        raise Exception('transfer_list ke %s harus memiliki transfer_type antara oversized_transfer atau undersized_transfer' % (i))
    return True


def _validationInput(args):
    # origin pond id validation
    origin_pond_id = args['origin_pond_id']
    if (origin_pond_id == None):
        raise Exception('Pond_id Tidak boleh kosong')
    pond = Pond.objects(id=origin_pond_id).first()
    if (not pond):
        raise Exception('Pond_id Tidak ditemukan')
    if (pond.isActive == False):
        raise Exception('Pond Tidak dalam musim budidaya')
    # fish sort type
    fish_sort_type = args['fish_sort_type']
    if (fish_sort_type != 'basah' and fish_sort_type != 'kering'):
        raise Exception("fish_sort_type harus berisi 'basah' atau 'kering'")
    # transfer list
    transfer_list_str = args['transfer_list']
    print('sampai sini')
    print(transfer_list_str)
    transfer_list = json.loads(transfer_list_str)
    if (len(transfer_list)<1):
        raise Exception('transfer_list harus lebih dari 1 kolam')
    # item transfer list
    for i in range(len(transfer_list)) :
        validation = _transferListValidation(i,transfer_list[i]);
        if validation :
            print ("berhasil validasi list ke %s" % (i))
        else :
            print ("gagal validasi list ke %s" % (i))
    return True

def createFishTransfer(origin_activation, destination_activation, args, transfer):
    return FishTransfer(**{
        "origin_pond_id": args['origin_pond_id'],
        "destination_pond_id": transfer['destination_pond_id'],
        "origin_activation_id": origin_activation.id,
        "destination_activation_id": destination_activation.id,
        "transfer_method": args['fish_sort_type'],
        "transfer_type": transfer['transfer_type'],
        "sample_weight": transfer['sample_weight'],
        "sample_long": transfer['sample_long'],
        "transfer_at": args['transfer_at']
    }).save(using=current_app.config['CONNECTION'])

def activationPond(args,transfer, isFishLogUpdate=True):
    pond = Pond.objects.get(id=transfer['destination_pond_id'])
    pipeline_year = {'$match': {'$expr': {'$and': [
                    {'$eq': ['$pond_id', {'$toObjectId': pond.id}]},
                    {'$eq': [{'$dateToString': {
                        'format': "%Y", 'date': "$created_at"}}, getYearToday()]},
    ]
    }}}
    list_pond_year = PondActivation.objects.aggregate(pipeline_year)
    list_pond_year = list(list_pond_year)
    id_int = len(list_pond_year) + 1
    pond_activation = PondActivation(**{
        "id_int": id_int,
        "pond_id": transfer['destination_pond_id'],
        "isFinish": False,
        "isWaterPreparation": False,
        "water_level": args['water_level'],
        "activated_at": args['transfer_at']
    }).save(using=current_app.config['CONNECTION'])
    pond.update(**{"isActive": True,
    "status": "Aktif",  "pondDoDesc": "Belum Diukur", "pondPhDesc": "Belum Diukur", "pondPh": None, "pondDo": None, "pondTemp": None})
    if isFishLogUpdate:
        for item_fish in transfer['fish']:
            # save fish log
            data = {
                "pond_id": pond.id,
                "pond_activation_id": pond_activation.id,
                "type_log": "activation",
                "fish_type": item_fish['type'],
                "fish_amount": item_fish['amount'],
                "fish_total_weight": item_fish['weight']
            }
            fishlog = FishLog(**data).save(using=current_app.config['CONNECTION'])
    return pond_activation

def createFishOut(origin_activation, args, transfer, fishtransfer):
    for item_fish in transfer['fish']:
        # save fish log
        data = {
            "pond_id": args['origin_pond_id'],
            "pond_activation_id": origin_activation.id,
            "fish_transfer_id": fishtransfer.id,
            "type_log": "transfer_out",
            "fish_type": item_fish['type'],
            "fish_total_weight": int(item_fish['weight']) * -1,
            "fish_amount": int(item_fish['amount']) * -1
        }
        fishlog = FishLog(**data).save(using=current_app.config['CONNECTION'])
    return

def createFishIn(destination_activation, args, transfer, fishtransfer, type_log):
    for item_fish in transfer['fish']:
        # save fish log
        data = {
            "pond_id": transfer['destination_pond_id'],
            "pond_activation_id": destination_activation.id,
            "fish_transfer_id": fishtransfer.id,
            "type_log": type_log,
            "fish_type": item_fish['type'],
            "fish_total_weight": int(item_fish['weight']),
            "fish_amount": int(item_fish['amount'])
        }
        fishlog = FishLog(**data).save(using=current_app.config['CONNECTION'])
    return

def transform_fish_data(fish_alive):
    transformed_list = []

    for entry in fish_alive:
        transformed_entry = {
            'type': entry['fish_type'],
            'amount': entry['fish_amount'],
            'weight': 0  # Isi weight dengan nilai default 0
        }
        transformed_list.append(transformed_entry)

    return transformed_list

def calculatedFish(transfer_list):
    fish_summary = []

    for transfer in transfer_list:
        fish_data = transfer['fish']
        for fish_entry in fish_data:
            fish_type = fish_entry['type']
            amount = fish_entry['amount']
            weight = fish_entry['weight']

            existing_fish = next((fish for fish in fish_summary if fish['type'] == fish_type), None)
            if existing_fish:
                existing_fish['amount'] += amount
                existing_fish['weight'] += weight
            else:
                fish_summary.append({"type": fish_type, "amount": amount, "weight": weight})


    return fish_summary

def calculatedFishDeath(args, fish_transfer):
    origin_activation = PondActivation.objects(pond_id=args['origin_pond_id'], isFinish=False).order_by('-activated_at').first()
    fish_alive = []
    fish_alive_obj = FishLog.objects.aggregate([{'$match': {
                                '$expr': {'$and': [
                                    {'$eq': ['$pond_activation_id',
                                     {'$toObjectId': origin_activation.id}]},
                                    {'$ne': ['$type_log', 'deactivation']},
                                ]}
                            }},
                            {"$project": {
                                "created_at": 0,
                                "updated_at": 0,
                            }},
                            {"$group": {
                                "_id": "$fish_type",
                                "fish_type": {"$first": "$fish_type"},
                                "fish_amount": {"$sum": "$fish_amount"}
                            }},
                            {"$sort": {"fish_type": -1}},
                            {"$project": {
                                "_id": 0,
                            }},])
    for fish in fish_alive_obj:
        fish_alive.append(fish)
    fish_alive = transform_fish_data(fish_alive=fish_alive)

    # fish alive - fish transfer
    fish_death = calculate_amount_difference(fish_alive, fish_transfer) 
    return fish_death

def calculate_amount_difference(fish_alive, fish_transfer):
    result = []

    for entry1, entry2 in zip(fish_alive, fish_transfer):
        print("entry1")
        print(entry1['amount'])
        print("entry2")
        print(entry2['amount'])

        diff_amount = entry1['amount'] - entry2['amount']
        result_entry = {
            'type': entry1['type'],
            'amount': diff_amount,
            'weight': entry1['weight']
        }
        result.append(result_entry)

    return result

def addfishdeath(args, fish_death_summary):
    origin_pond = Pond.objects.get(id=args['origin_pond_id'])
    origin_pond_activation = PondActivation.objects(pond_id=args['origin_pond_id'], isFinish=False).order_by('-activated_at').first()
    fishdeath = FishDeath(**{
        "pond_id": origin_pond.id,
        "pond_activation_id": origin_pond_activation.id,
        "image_name": "default.jpg",
        "diagnosis": "selisih saat sortir ikan",
        "death_at": datetime.datetime.now
    }).save(using=current_app.config['CONNECTION'])
    for fish in fish_death_summary:
        # save fish log
        fishlog = FishLog(**{
            "pond_id": origin_pond.id,
            "pond_activation_id": origin_pond_activation.id,
            "fish_death_id": fishdeath.id,
            "type_log": "death",
            "fish_type": fish['type'],
            "fish_amount": int(fish['amount']) * -1
        }).save(using=current_app.config['CONNECTION'])
    return

def deactivationPond(args):
    pond_activation = PondActivation.objects(pond_id=args['origin_pond_id'], isFinish=False).order_by('-activated_at').first()
    pond_activation = pond_activation.update(**{
        "isFinish": True,
        "total_fish_harvested": args['total_fish_harvested'],
        "total_weight_harvested": args['total_weight_harvested'],
        "deactivated_at": datetime.datetime.now(),
        "deactivated_description": "Sortir Ikan",
        "amount_undersize_fish":args['amount_undersize'],
        "amount_oversize_fish":args['amount_oversize'],
        "amount_normal_fish":args['amount_normal'],
        "sample_amount":args['sample_amount'],
        "sample_long":args['sample_long'],
        "sample_weight": args['sample_weight']
    })
    pond = Pond.objects.get(id=args['origin_pond_id'])
    pond = pond.update(**{"isActive": False,
        "status": "Aktif",  "pondDoDesc": "Belum Diukur", "pondPhDesc": "Belum Diukur", "pondPh": None, "pondDo": None, "pondTemp": None})
    # create fish log deactivation

    return pond_activation


class FishSortsApi(Resource):
    def post(self):
        # try:
            parser = reqparse.RequestParser()
            parser.add_argument('origin_pond_id', type=str, required=True, location='form')
            parser.add_argument('fish_sort_type', type=str, required=True, location='form')
            parser.add_argument('transfer_list', type=str, required=False, location='form')
            parser.add_argument('fish_death', type=str, required=False, location='form')
            parser.add_argument('transfer_at', type=str, required=False, location='form')
            parser.add_argument('water_level', type=int, required=False, default=1, location='form')
            parser.add_argument("amount_undersize", type=int, required=False, default=0, location='form')
            parser.add_argument("amount_oversize",type=int, required=False, default=0, location='form')
            parser.add_argument("amount_normal",type=int, required=False, default=0, location='form')
            parser.add_argument("sample_weight",type=int, required=False, default=0, location='form')
            parser.add_argument("sample_amount",type=int, required=False, default=0, location='form')
            parser.add_argument("sample_long",type=int, required=False, default=0, location='form')
            parser.add_argument("total_fish_harvested",type=int, required=False, default=0, location='form')
            parser.add_argument("total_weight_harvested",type=int, required=False, default=0, location='form')
            parser.add_argument('fish_death', type=str, required=False, location='form')
            # print("", location='form')
            args = parser.parse_args()
            print(args)
            # validation = _validationInput(args)
            # if (not validation):
            #     raise Exception("Input gagal di validasi")
            # create dict of transfer_list
            transfer_list_str = args['transfer_list']
            transfer_list = json.loads(transfer_list_str)
            # test
            # print('disini')
            # fish_transfer = calculatedFish(transfer_list=transfer_list)
            # print('disini fish_transfer')
            # print(fish_transfer)
            # print('disini fish_Death')
            # print(calculatedFishDeath(args, fish_transfer))
            # check if sort type
            if (args['fish_sort_type']== 'basah'):
                # create fish transfer per transfer_list
                for transfer in transfer_list:
                    if (transfer['status'] == 'isActivated'):
                        # get origin activation
                        origin_activation = PondActivation.objects(pond_id=args['origin_pond_id'], isFinish=False).order_by('-activated_at').first()
                        # get destination activation
                        destination_activation = PondActivation.objects(pond_id=transfer['destination_pond_id'], isFinish=False).order_by('-activated_at').first()
                        # create fishtransfer
                        fishtransfer = createFishTransfer(origin_activation, destination_activation, args, transfer)
                        # transfer out
                        createFishOut(origin_activation, args, transfer, fishtransfer)
                        # transfer in
                        createFishIn(destination_activation, args, transfer, fishtransfer,"transfer_in")
                    if (transfer['status'] == 'isNotActivated'):
                        # get origin activation
                        origin_activation = PondActivation.objects(pond_id=args['origin_pond_id'], isFinish=False).order_by('-activated_at').first()
                        # activation pond destination
                        destination_activation = activationPond(args, transfer)
                        # create fishtransfer
                        fishtransfer = createFishTransfer(origin_activation, destination_activation, args, transfer)
                        # transfer out
                        createFishOut(destination_activation, args, transfer, fishtransfer)
            if (args['fish_sort_type']== 'kering'):
                # create fish transfer per transfer_list
                for transfer in transfer_list:
                    if (transfer['destination_pond_id'] == args['origin_pond_id']):
                        continue 
                    if (transfer['status'] == 'isActivated'):
                        # get origin activation
                        origin_activation = PondActivation.objects(pond_id=args['origin_pond_id'], isFinish=False).order_by('-activated_at').first()
                        # get destination activation
                        destination_activation = PondActivation.objects(pond_id=transfer['destination_pond_id'], isFinish=False).order_by('-activated_at').first()
                        # create fishtransfer
                        fishtransfer = createFishTransfer(origin_activation, destination_activation, args, transfer)
                        # transfer in
                        createFishIn(destination_activation, args, transfer, fishtransfer,"transfer_in")
                    if (transfer['status'] == 'isNotActivated'):
                        # get origin activation
                        origin_activation = PondActivation.objects(pond_id=args['origin_pond_id'], isFinish=False).order_by('-activated_at').first()
                        # activation pond destination
                        destination_activation = activationPond(args, transfer, isFishLogUpdate=False)
                        # create fishtransfer
                        fishtransfer = createFishTransfer(origin_activation, destination_activation, args, transfer)
                        # transfer out for destination_activation
                        createFishIn(destination_activation, args, transfer, fishtransfer, "activation")
                # calculated fish all pond
                fish_summary = calculatedFish(transfer_list)
                # calculated fish death
                fish_death_summary = calculatedFishDeath(args,fish_summary)
                # add fish death
                addfishdeath(args,fish_death_summary)
                # deactivation origin pond
                deactivationPond(args)
                for transfer in transfer_list:
                    if (transfer['destination_pond_id'] == args['origin_pond_id']):
                        # get origin activation
                        last_origin_activation = PondActivation.objects(pond_id=args['origin_pond_id']).order_by('-activated_at').first()
                        # activation pond with same fish
                        origin_pond_activation = activationPond(args, transfer)
            response = {"message": "success add multipond fish sort"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        # except Exception as e:
        #     response = {"message": str(e)}
        #     response = json.dumps(response, default=str)
        #     return Response(response, mimetype="application/json", status=400)