from flask_restful import Resource, Api, marshal_with, fields, abort
from flask_restful_swagger import swagger

@swagger.model
class DummyResult(object):
    """The result of a call to /dummy"""
    resource_fields = {
        'dummy': fields.String
    }

    def __init__(self):
        self.dummy = "foobar"


@swagger.model
class HelloResult(object):
    """The result of a call to /hello"""
    resource_fields = {
        'greetings': fields.String
    }

    def __init__(self, name):
        self.greetings = "Hello {}".format(name)

@swagger.model
class AnalysisResult:
    """The result of a call to /analyze"""
    file_fields = {
        'filename': fields.String,
        'status': fields.String,
        'message': fields.String,
        'num_pages': fields.Integer,
        'positive': fields.List(fields.Integer)
    }
    resource_fields = {
        'num_files': fields.Integer,
        'results': fields.List(fields.Nested(file_fields))
    }

    def __init__(self, results):
        self.num_files = len(results)
        self.results = results