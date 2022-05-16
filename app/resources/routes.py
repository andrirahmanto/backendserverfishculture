from .controller.feedhistory import FeedHistorysApi, FeedHistoryApi, FeedHistoryTodayByPond, FeedHistoryTodayByOnePond, FeedHistoryMonthByPond
from .controller.pond import PondsApi, PondApi
from .controller.feedtype import FeedTypesApi, FeedTypeApi


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
    api.add_resource(FeedHistoryTodayByPond,
                     '/api/feedhistorybypond/day')
    api.add_resource(FeedHistoryTodayByOnePond,
                     '/api/feedhistorybyonepond/<id>')
    api.add_resource(FeedHistoryMonthByPond,
                     '/api/feedhistorybypond/month')
