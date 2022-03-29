from .logfeeding import LogFeedingsApi, LogFeedingApi
from .pond import PondsApi, PondApi
from .typefeed import TypeFeedsApi, TypeFeedApi


def initialize_routes(api):

    # pond
    api.add_resource(PondsApi, '/api/ponds')
    api.add_resource(PondApi, '/api/ponds/<id>')

    # typefeed
    api.add_resource(TypeFeedsApi, '/api/typefeeds')
    api.add_resource(TypeFeedApi, '/api/typefeeds/<id>')

    # logfeeding
    api.add_resource(LogFeedingsApi, '/api/logfeedings')
    api.add_resource(LogFeedingApi, '/api/logfeedings/<id>')
