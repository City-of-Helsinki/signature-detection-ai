import itertools
import numpy as np
import PIL


def get_tiles(image: PIL.Image.Image, tile_size: int):
    # Get a list of tile extents given the tile size
    n_x, n_y = int(np.ceil(image.width/tile_size)), int(np.ceil(image.height/tile_size))
    offset_x = np.linspace(0, image.width-tile_size, n_x).astype(int)
    offset_y = np.linspace(0, image.height-tile_size, n_y).astype(int)
    positions = [{'x_start': x, 
                  'x_stop': x+tile_size, 
                  'y_start': y, 
                  'y_stop': y+tile_size} 
                  for x,y in itertools.product(offset_x, offset_y)]
    return positions


def expand_image(image:PIL.Image.Image, minimum_width:int, minimum_height:int):
    # Returns the image with padding as necessary to reach minimum
    # width and height
    if image.width < minimum_width or image.height < minimum_height:
        new_width = max(image.width, minimum_width)
        new_height = max(image.height, minimum_height)
        image = PIL.ImageOps.pad(image, 
                                 size=(new_width, new_height),
                                 color=(255,255,255),
                                 centering=(0,0))
    return image
