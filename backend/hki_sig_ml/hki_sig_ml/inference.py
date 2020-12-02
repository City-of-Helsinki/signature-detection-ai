from pathlib import Path

import numpy as np

from fastai.data.block import DataBlock, CategoryBlock
from fastai.data.transforms import ItemGetter
from fastai.learner import Learner
from fastai.vision.data import ImageBlock
from fastai.vision.learner import cnn_learner
from fastai.vision.core import PILImage

import pandas as pd

import PIL

import pdf2image

from torch import nn
from torchvision.models import resnet18, resnet34, mobilenet_v2

from .utils import expand_image, get_tiles

def split_documents(pdf_documents:list, dpi:int=50):
    # Split each page into square tiles with side length equal to
    # A4 width
    a4_width = 8.3
    dpi = 50
    tile_size = int(a4_width*dpi)
    info = []
    tiles = []
    errors = []
    
    for i, pdf in enumerate(pdf_documents):
        try:
            pages = pdf2image.convert_from_bytes(pdf['bytes'], dpi=dpi)
            for j, page in enumerate(pages):
                page = expand_image(page, tile_size, tile_size)
                for k, tile in enumerate(get_tiles(page, tile_size)):
                    tile = [tile['x_start'], tile['y_start'], 
                            tile['x_stop'], tile['y_stop']]
                    info.append({'document': pdf['filename'], 
                                 'page': j+1, 
                                 'tile': k+1, 
                                 'tile_extent': tile})
                    tiles.append(PILImage.create(np.array(page.crop(tile))))
        except Exception as e:
            errors.append({'document': pdf['filename'], 'error': e})
            print('Unable to open', pdf['filename'], 'because', e)
            
    return tiles, pd.DataFrame(info), pd.DataFrame(errors)


def _mobilenetv2_split(m:nn.Module): return (m[0][0][10],m[1])


def create_inference_model(checkpoint:str=None, model='resnet34', path='.'):
    if model == 'resnet34':
        model = resnet34
    elif model == 'resnet18':
        model = resnet18
    elif model == 'mobilenet_v2':
        model = mobilenet_v2

    # Create an inference model instance and load the requested checkpoint
    inf_db = DataBlock(blocks=[ImageBlock, CategoryBlock], 
                       get_x=ItemGetter(0),
                       get_y=ItemGetter(1))

    dummy_img = PILImage.create(np.zeros((415,415,3), 
                                dtype=np.uint8))
    source = [(dummy_img, False), 
              (dummy_img, True)]
    
    inf_dls = inf_db.dataloaders(source)

    if model == mobilenet_v2:
        learner = cnn_learner(inf_dls, model, cut=-1, splitter=_mobilenetv2_split, pretrained=False)
    else:
        learner = cnn_learner(inf_dls, model, pretrained=False)
    learner.path = Path(path)

    if checkpoint is not None:
        learner.load(checkpoint, with_opt=False, device='cpu')

    return learner


def predict(pdf_tiles:list, learner:Learner):
    # Get predicted labels and confidences for the given image tiles
    predictions = [learner.predict(tile) for tile in pdf_tiles]
    labels = [prediction[0] for prediction in predictions]
    confidences = [float(prediction[2][prediction[1]].numpy()) 
                   for prediction in predictions]
    return labels, confidences


def distill_results(df: pd.DataFrame, errors: pd.DataFrame=None):
    res = {}
    for i,row in df.iterrows():
        index = row.document
        # If we haven't seen this page before, include it in the
        # distilled results
        if index not in res:
            res[index] = {'document': row.document,
                          'status': 'OK',
                          'message': '',
                          'num_pages': 1,
                          'positive': [row.page] if row.label == 'True' else []}
        else:
            new_pages = res[index]['num_pages'] if row.page <= res[index]['num_pages'] else row.page
            if row.label == 'True' and int(row.page):
                new_positives = res[index]['positive'] + [int(row.page)]
            else:
                new_positives = res[index]['positive']
            res[index] = {**res[index],
                          'num_pages': int(new_pages),
                          'positive': sorted(list(set(new_positives)))}
            
    if errors is not None:
        for i,row in errors.iterrows():
            res.append({'document': row.document, 
                        'status': 'ERROR', 
                        'message': '', 
                        'num_pages': -1, 
                        'positive': []})
            
    return pd.DataFrame(res.values())


def distill_details(info: pd.DataFrame, errors: pd.DataFrame=None):
    # Aggregate predictions over tiles
    res = {}
    for i,row in info.iterrows():
        index = (row.document, row.page)
        # If we haven't seen this page before, include it in the
        # distilled results
        if index not in res:
            res[index] = {'document': row.document,
                          'status': 'OK',
                          'page': row.page,
                          'label': row.label,
                          'confidence': row.confidence}
        # If we think we've found a signature, switch the page classification
        if res[index]['label'] == 'False' and row.label == 'True':
            res[index] = {**res[index],
                          'label': row.label,
                          'confidence': row.confidence}
        # A no signature page confidence is the lowest confidence
        # found
        if res[index]['label'] == row.label == 'False' and res[index]['confidence'] > row.confidence:
            res[index] = {**res[index],
                          'confidence': row.confidence}
        # A signature page confidence is the highest confidence
        # found
        if res[index]['label'] == row.label == 'True' and res[index]['confidence'] < row.confidence:
            res[index] = {**res[index],
                          'confidence': row.confidence}
            
    if errors is not None:
        for i,row in errors.iterrows():
            res[(row.document,)] = {'document': row.document, 
                                    'status': 'ERROR'}
            
    df = pd.DataFrame(res.values())
    df = df.fillna('-')

    return df

def classify(pdf_documents: list, learner:Learner):
    tiles, info, errors = split_documents(pdf_documents)
    print('Got', len(tiles), 'tiles')

    labels, confidences = predict(tiles, learner)

    info['label'] = labels
    info['confidence'] = confidences

    results = distill_results(info, errors)
    details = distill_details(info, errors)

    return results, details

