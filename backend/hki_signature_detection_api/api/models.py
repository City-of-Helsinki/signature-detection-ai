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
        'document': fields.String,
        'status': fields.String,
        'message': fields.String,
        'num_pages': fields.Integer,
        'positive': fields.List(fields.Integer)
    }
    detail_fields = {
        'document': fields.String,
        'status': fields.String,
        'page': fields.Integer,
        'label': fields.String,
        'confidence': fields.Float,
    }
    resource_fields = {
        'num_files': fields.Integer,
        'results': fields.List(fields.Nested(file_fields)),
        'details': fields.List(fields.Nested(detail_fields)),
        'csv': fields.Raw,
        'classification_duration': fields.Float,
    }

    def __init__(self, results, details, csv, classification_duration):
        self.num_files = len(results)
        self.results = results
        self.details = details
        self.csv = csv
        self.classification_duration = classification_duration