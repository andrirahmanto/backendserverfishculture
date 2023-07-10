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
    'origin_pond_id': 'obid(1288374682374)',
    'fish_sort_type' : 'kering',
    'total_fish_harvested' : 330,
    'amount_undersize' : 10,
    'amount_oversize' : 20,
    'amount_normal' : 300,
    'sample_weight' : 400,
    'sample_amount' : 60,
    'sample_long' : 50,
    'total_weight_harvested' : 3000,
    'transfer_list' : [
        {
            'destination_pond_id':'obid(1288374682374)',
            'status': 'isActivated',
            'fish': [
                {"type": "lele","amount": 5, "weight":23},
                {"type": "patin","amount": 9, "weight":23}
            ],
            'sample_weight': 20,
            'sample_long': 20,
            'transfer_type': 'oversized_transfer'
        },
        {
            'destination_pond_id':'obid(1288374682374)',
            'activation_type' : 'pedaging',
            'status': 'isNotActivated',
            'water_level': 100,
            'fish': [
                {"type": "lele","amount": 5, "weight":23},
                {"type": "patin","amount": 9, "weight":23}
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
    if (transfer['transfer_type'] != "oversized_transfer" and transfer['transfer_type'] != "undersized_transfer"):
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
    }).save()

def activationPond(args,transfer):
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
    }).save()
    pond.update(**{"isActive": True,
    "status": "Aktif",  "pondDoDesc": "Belum Diukur", "pondPhDesc": "Belum Diukur", "pondPh": None, "pondDo": None, "pondTemp": None})
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
        fishlog = FishLog(**data).save()
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
        fishlog = FishLog(**data).save()
    return

def createFishIn(destination_activation, args, transfer, fishtransfer):
    for item_fish in transfer['fish']:
        # save fish log
        data = {
            "pond_id": transfer['destination_pond_id'],
            "pond_activation_id": destination_activation.id,
            "fish_transfer_id": fishtransfer.id,
            "type_log": "transfer_in",
            "fish_type": item_fish['type'],
            "fish_total_weight": int(item_fish['weight']),
            "fish_amount": int(item_fish['amount'])
        }
        fishlog = FishLog(**data).save()
    return

def deactivationPond(args):
    pond_activation = pond_activation.update(**{
        "isFinish": True,
        "total_fish_harvested": total_fish_harvested,
        "total_weight_harvested": total_weight_harvested,
        "deactivated_at": datetime.datetime.now(),
        "deactivated_description": "Sortir Ikan",
        "amount_undersize_fish":amount_undersize,
        "amount_oversize_fish":amount_oversize,
        "amount_normal_fish":amount_normal,
        "sample_amount":sample_amount,
        "sample_long":sample_long,
        "sample_weight": sample_weight
    })
    return pond_activation


class FishSortsApi(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('origin_pond_id', type=str, required=True, location='form')
            parser.add_argument('fish_sort_type', type=str, required=True, location='form')
            parser.add_argument('transfer_list', type=str, required=False, location='form')
            parser.add_argument('fish_death', type=str, required=False, location='form')
            parser.add_argument('transfer_at', type=str, required=False, location='form')
            parser.add_argument('water_level', type=str, required=False, default=1, location='form')
            parser.add_argument("amount_undersize", required=False, default=0, location='form')
            parser.add_argument("amount_oversize", required=False, default=0, location='form')
            parser.add_argument("amount_normal", required=False, default=0, location='form')
            parser.add_argument("sample_weight", required=False, default=0, location='form')
            parser.add_argument("sample_amount", required=False, default=0, location='form')
            parser.add_argument("sample_long", required=False, default=0, location='form')
            parser.add_argument("total_fish_harvested", required=False, default=0, location='form')
            parser.add_argument("total_weight_harvested", required=False, default=0, location='form')
            # print("", location='form')
            args = parser.parse_args()
            print(args)
            validation = _validationInput(args)
            if (not validation):
                raise Exception("Input gagal di validasi")
            # create dict of transfer_list
            transfer_list_str = args['transfer_list']
            transfer_list = json.loads(transfer_list_str)
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
                        createFishIn(destination_activation, args, transfer, fishtransfer)
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
                    if (transfer['status'] == 'isActivated'):
                        # get origin activation
                        origin_activation = PondActivation.objects(pond_id=args['origin_pond_id'], isFinish=False).order_by('-activated_at').first()
                        # get destination activation
                        destination_activation = PondActivation.objects(pond_id=transfer['origin_pond_id'], isFinish=False).order_by('-activated_at').first()
                        # create fishtransfer
                        fishtransfer = createFishTransfer(origin_activation, destination_activation, args, transfer)
                        # transfer out
                        createFishOut(origin_activation, args, transfer, fishtransfer)
                        # transfer in
                        createFishIn(destination_activation, args, transfer, fishtransfer)
                    if (transfer['status'] == 'isNotActivated'):
                         # get origin activation
                        origin_activation = PondActivation.objects(pond_id=args['origin_pond_id'], isFinish=False).order_by('-activated_at').first()
                        # activation pond destination
                        destination_activation = activationPond(args, transfer)
                        # create fishtransfer
                        fishtransfer = createFishTransfer(origin_activation, destination_activation, args, transfer)
                        # transfer out
                        createFishOut(destination_activation, args, transfer, fishtransfer)
                    # deactivation origin pond
                    deactivationPond(args)
            response = {"message": "success add multipond fish sort"}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=200)
        except Exception as e:
            response = {"message": str(e)}
            response = json.dumps(response, default=str)
            return Response(response, mimetype="application/json", status=400)