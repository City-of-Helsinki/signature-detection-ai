import io
import itertools
from pathlib import Path
import random

from fastai.data.block import TransformBlock
from fastai.data.transforms import get_files, IntToFloatTensor
from fastai.torch_core import TensorCategory
from fastai.vision.core import PILImage
from fastcore.foundation import L
from fastcore.transform import ItemTransform
from joblib import Memory
import numpy as np
from pdf2image import convert_from_path
from PIL import Image, ImageFilter
import scipy.stats
from tqdm import tqdm
from cairosvg import svg2png


#memory = Memory('.joblib_cache')
#convert_pdf = memory.cache(convert_from_path, verbose=0)
convert_pdf = convert_from_path

def get_tiles(image: Image, tile_size: int):
    n_x, n_y = int(np.ceil(image.width/tile_size)), int(np.ceil(image.height/tile_size))
    offset_x = np.linspace(0, image.width-tile_size, n_x).astype(int)
    offset_y = np.linspace(0, image.height-tile_size, n_y).astype(int)
    positions = [{'x_start': x, 
                  'x_stop': x+tile_size, 
                  'y_start': y, 
                  'y_stop': y+tile_size} 
                 for x, y in itertools.product(offset_x, offset_y)]
    return positions


def get_document_tiles(pdf_directory, dpi=50):
    pdf_files = get_files(pdf_directory, extensions=['.pdf'])

    # Split each page into square tiles with side length equal to
    # A4 width
    a4_width = 8.3
    dpi = 50
    tile_size = int(a4_width*dpi) 
    pdf_tiles = []

    #print(f'Checking PDF files in {pdf_directory}', flush=True)
    for pdf in tqdm(pdf_files):
        try:
            pages = convert_from_path(pdf, dpi=dpi)
            for i, page in enumerate(pages):
                for j, tile in enumerate(get_tiles(page, tile_size)):
                    pdf_tiles.append({'path': pdf, 
                                      'page': i, 
                                      'size': [page.width, page.height],
                                      'tile': j,
                                      'tile_edges': tile})
        except Exception as error:
            print('Unable to open', pdf, 'because', error)
   
    dummy_labels = np.zeros(len(pdf_tiles)).astype(int)
    dummy_labels[-1] = 1
    #return pdf_tiles
    return list(zip(pdf_tiles, dummy_labels))


def get_svg_signatures(svg_directory, verbose=False):
    svg_files = get_files(svg_directory, extensions=['.svg'])
    ok_files = []
    print(f'Checking SVG files in {svg_directory}', flush=True)
    for svg_path in tqdm(svg_files):
        try:
            img = Image.open(io.BytesIO(svg2png(url=str(svg_path))))
            
            if img.mode != 'RGBA':
                if verbose:
                    print(f'Discarding {svg_path} because it is missing an alpha channel (image mode {img.mode})')
                continue
            if (np.array(img.getchannel('A'))/255).mean() > 0.2:
                if verbose:
                    print(f'Discarding {svg_path} because more than 20% of the alpha channel is white')
                continue
                
            aspect_ratio = img.height/img.width
            ok_files.append({'path': svg_path, 'aspect_ratio': aspect_ratio})
        except Exception as e:
            print('Unable to open', svg_path, 'because', e)
    return L(ok_files)


def get_signature_image(svg_spec: dict, width: int=100, prob_rotate: float=1.0,
                        prob_colorize: float=0.5, prob_erode: float=0.0, 
                        prob_dilate: float=0.05):
    img = Image.open(io.BytesIO(svg2png(url=str(svg_spec['path']),
                                        output_width=width,
                                        output_height=int(width*svg_spec['aspect_ratio']))))

    assert img.mode == 'RGBA', f'Image {svg_spec["path"]} does not have alpha channel'
    alpha = img.getchannel('A')

    # Erosion
    if random.random() < prob_dilate:
        alpha = alpha.filter(ImageFilter.MaxFilter(3))

    # Dilation
    if random.random() < prob_erode:
        alpha = alpha.filter(ImageFilter.MinFilter(3))

    # Rotation
    # Choose angle randomly, but with high weight around 0+-x, and lower weight
    # around -90/90/180+-x
    if random.random() < prob_rotate:
        loc = np.random.choice([0, -np.pi/2, np.pi/2, np.pi], p=[2/3, 1/9, 1/9, 1/9])
        angle = scipy.stats.vonmises.rvs(loc=loc, kappa=4)*(180/np.pi)
        alpha = alpha.rotate(angle, resample=Image.BICUBIC, expand=True)

    # Colorize
    # Choose color randomly by sampling each channel randomly from a PDF that
    # decreases linearly from 0 to 255
    if random.random() < prob_colorize:
        color = tuple((scipy.stats.triang.rvs(size=3, loc=0, c=0, scale=1)*255).astype(int))
        bg = Image.new(mode='RGBA', size=alpha.size, color=color)
    else:
        bg = Image.new(mode='RGBA', size=alpha.size, color='black')
    bg.putalpha(alpha)
 
    return bg


def create_synthetic_image(doc_spec: dict, svg_specs: list, positive_prob: float=0.5, 
                           dpi: int=50) -> None:
    #print(doc_spec)
    doc_img = convert_pdf(pdf_path=doc_spec['path'],
                          dpi=dpi,
                          first_page=doc_spec['page']+1,
                          last_page=doc_spec['page']+1)[0]
    tile = doc_spec['tile_edges']
    tile = [tile['x_start'], tile['y_start'], tile['x_stop'], tile['y_stop']]
    doc_img = doc_img.crop(tile)
    #svg_files = get_svg_signatures(svg_directory)
    label = 0
    if random.random() < positive_prob:
        width_in = scipy.stats.uniform.rvs(loc=0.5, scale=4)
        width = int(width_in*dpi)
        #print('random sample', random.sample(svg_specs, k=1)[0])
        sig_img = get_signature_image(random.sample(svg_specs, k=1)[0], width=width)

        x = random.randint(-sig_img.width//2, doc_img.width-sig_img.width//2)
        y = random.randint(-sig_img.height//2, doc_img.height-sig_img.height//2)
        doc_img.paste(sig_img, [x,y], sig_img)
        label = 1

    return (PILImage.create(np.array(doc_img)), TensorCategory(label))


def create_tile_image(doc_spec: dict, dpi: int=50) -> None:
    doc_img = convert_pdf(pdf_path=doc_spec['path'],
                          dpi=dpi,
                          first_page=doc_spec['page']+1,
                          last_page=doc_spec['page']+1)[0]
    tile = doc_spec['tile_edges']
    tile = [tile['x_start'], tile['y_start'], tile['x_stop'], tile['y_stop']]
    doc_img = doc_img.crop(tile)

    return (PILImage.create(np.array(doc_img)), TensorCategory(0))


def SyntheticImageBlock(svg_directory: Path, positive_prob: float = 0.5):
    svg_specs = get_svg_signatures(svg_directory)
    return TransformBlock(type_tfms=lambda doc_spec: create_synthetic_image(doc_spec, svg_specs, positive_prob), 
                          batch_tfms=IntToFloatTensor)


def TileImagTransformBlock():
    return TransformBlock(type_tfms=create_tile_image, batch_tfms=IntToFloatTensor)


class GetLabelFromX(ItemTransform):
    def encodes(self, item):
        #print('Item is', item)
        return item[0]
    def decodes(self, item):
        #print('Decoding, item is', item)
        return item
