#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from PIL import Image
from io import BytesIO

from skimage.color import rgb2lab


class ImagePreprocessing():
    @staticmethod
    def convert_pil_image_to_grayscale(image: Image.Image) -> Image.Image:
        return image.convert('L')

    @staticmethod
    def convert_pil_image_to_png(image: Image.Image) -> BytesIO:
        png_buf = BytesIO()
        image.save(png_buf, format="PNG")
        return png_buf

    @staticmethod
    def convert_pil_image_to_jpeg(image: Image.Image, quality=80) -> BytesIO:
        jpeg_buf = BytesIO()
        image.save(jpeg_buf, format="JPEG", quality=quality)
        return jpeg_buf

    @staticmethod
    def convert_pil_image_to_lab(image: Image.Image) -> np.ndarray:
        return rgb2lab(np.array(image)).astype(np.float32)
