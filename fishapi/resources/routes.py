from .controller.feedhistory import *
from .controller.pond import *
from .controller.feedtype import *
from .controller.pondactivation import *
from .controller.fishdeath import *


def initialize_routes(api):

    # pond
    api.add_resource(PondsApi, '/api/ponds')
    api.add_resource(PondApi, '/api/ponds/<id>')
    api.add_resource(PondImageApi, '/api/ponds/image/<id>')
    api.add_resource(PondImageApiDummy, '/api/ponds/image')

    # pond status
    api.add_resource(PondsStatusApi, '/api/ponds/status')
    api.add_resource(PondStatusApi, '/api/ponds/status/<pond_id>')
    api.add_resource(PondActivationApi, '/api/ponds/<pond_id>/activation')
    api.add_resource(PondDeactivationApi, '/api/ponds/<pond_id>/deactivation')

    # feedtype
    api.add_resource(FeedTypesApi, '/api/feedtypes')
    api.add_resource(FeedTypeApi, '/api/feedtypes/<id>')

    # feedhistory
    api.add_resource(FeedHistorysApi, '/api/feedhistorys')
    api.add_resource(FeedHistoryApi, '/api/feedhistorys/<id>')
    api.add_resource(FeedHistoryByPond,
                     '/api/feedhistorysbypond')
    api.add_resource(FeedHistoryByOnePond,
                     '/api/feedhistorysbyonepond/<id>')

    # fish death
    api.add_resource(FishDeathsApi, '/api/fishdeath')
    api.add_resource(FishDeathApi, '/api/fishdeath/<id>')
    api.add_resource(FishDeathImageApi, '/api/fishdeath/image/<id>')
    api.add_resource(FishDeathImageApiDummy, '/api/fishdeath/image')
