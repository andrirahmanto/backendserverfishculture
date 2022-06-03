from .controller.feedhistory import *
from .controller.pond import *
from .controller.feedtype import *


def initialize_routes(api):

    # pond
    api.add_resource(PondsApi, '/api/ponds')
    api.add_resource(PondApi, '/api/ponds/<id>')

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
