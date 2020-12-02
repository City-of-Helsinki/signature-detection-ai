from flask import Flask, request
from flask_restful import Resource, Api, marshal_with, fields, abort
from flask_restful_swagger import swagger
from flask_cors import CORS
from hki_signature_detection_api.api import DummyEndpoint
from hki_signature_detection_api.api import HelloEndpoint
from hki_signature_detection_api.api import AnalysisEndpoint

API_VERSION_NUMBER = '1.0'
API_VERSION_LABEL = 'v1'


class SignatureDetectionApiApp:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        custom_errors = {
            'JsonInvalidError': {
                'status': 500,
                'message': 'JSON format not valid'
            },
            'JsonRequiredError': {
                'status': 400,
                'message': 'JSON input required'
            }
        }
        self.api = swagger.docs(Api(self.app, errors=custom_errors), apiVersion=API_VERSION_NUMBER)
        
        #self.api.add_resource(DummyEndpoint, '/dummy', endpoint='dummy')
        #self.api.add_resource(HelloEndpoint, '/hello', endpoint='hello')
        self.api.add_resource(AnalysisEndpoint, '/analyze', endpoint='analyze')

    def run(self, *args, **kwargs):
        self.app.config['PROPAGATE_EXCEPTIONS'] = False
        self.app.run(*args, **kwargs)


def run_app(*args, **kwargs):
    app = SignatureDetectionApiApp()
    app.run(*args, **kwargs)


if __name__ == '__main__':
    run_app(debug=True)