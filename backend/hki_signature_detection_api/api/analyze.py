import random

from flask import request
from flask_restful import Resource, Api, marshal_with, fields, abort
from flask_restful_swagger import swagger
from PyPDF4.pdf import PdfFileReader
from PyPDF4.utils import PyPdfError

from .models import AnalysisResult

class AnalysisEndpoint(Resource):
    @swagger.operation(
        responseClass=AnalysisResult.__name__,
        nickname='analyze'
    )
    @marshal_with(AnalysisResult.resource_fields)
    def post(self):
        """Return a AnalysisResult object"""
        num_files = int(request.form['num_files'])
        print('num_files:', num_files)
        print('len(request.files):', len(request.files))
        
        results = []
        for filename, file_stream in request.files.items():
            try:
                pdf_reader = PdfFileReader(file_stream)
                num_pages = pdf_reader.getNumPages()
                results.append({
                    'filename': filename,
                    'status': 'OK',
                    'message': '',
                    'num_pages': num_pages,
                    'positive': random.choices(range(1,num_pages+1), k=5)
                })
            except PyPdfError as e:
                results.append({
                    'filename': filename,
                    'status': 'ERROR',
                    'message': e,
                    'num_pages': -1,
                    'positive': []
                })

        return AnalysisResult(results)