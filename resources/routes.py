from .logfeeding import LogFeedingsApi, LogFeedingApi


def initialize_routes(api):
    api.add_resource(LogFeedingsApi, '/api/logfeedings')
    api.add_resource(LogFeedingApi, '/api/logfeedings/<id>')
