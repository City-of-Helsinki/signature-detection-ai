import base64
import random
import time

from flask import request
from flask_restful import Resource, Api, marshal_with, fields, abort
from flask_restful_swagger import swagger
from PyPDF4.pdf import PdfFileReader
from PyPDF4.utils import PyPdfError

from hki_sig_ml.inference import create_inference_model, classify

from .models import AnalysisResult

learner = create_inference_model('resnet18_lean', path='/app', model='resnet18')

class AnalysisEndpoint(Resource):
    @swagger.operation(
        responseClass=AnalysisResult.__name__,
        nickname='analyze'
    )
    @marshal_with(AnalysisResult.resource_fields)
    def post(self):
        """Return a AnalysisResult object"""
        # Get PDF documents
        pdf_documents = [{'filename': filename, 'bytes': file_stream.read()} for
            filename, file_stream in request.files.items()]

        # Classify pages
        t0 = time.time()
        results, details = classify(pdf_documents, learner)
        classification_duration = time.time() - t0

        # Package results in CSV
        csv = base64.b64encode(details.to_csv().encode('utf-8')).decode('ascii')
        csv = f'data:text/csv;base64,{csv}'
        
        # Package results to dict
        results = results.to_dict(orient='records')
        details = details.to_dict(orient='records')

        return AnalysisResult(results, details, csv, classification_duration)