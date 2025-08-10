#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Metric: PNG file size

Description: The file size of an image in bytes, saved in the PNG format (24 bits per pixel, RGB).

References:
    [1] A. Miniukovich and A. De Angeli (2015). Computation of Interface Aesthetics.
    CHI'15: Proceedings of the 33rd Annual ACM Conference on Human Factor in Computing Systems, pp. 1163-1172.
    DOI: https://doi.org/10.1145/2702123.2702575

    [2] E. Boychuk and M. Bakaev (2019). Entropy and Compression Based Analysis of Web User Interfaces.
    International Conference on Web Engineering (ICWE) 2019, pp. 253-261.
    DOI: https://doi.org/10.1007/978-3-030-19274-7_19
"""

from typing import Optional, Dict, Any, Union, List
from io import BytesIO

import numpy as np
from PIL import Image

from metrics_evaluator.metrics.metric_interface import MetricInterface
from pydantic import HttpUrl


class Metric(MetricInterface):
    def execute(
            self,
            pil_image: Optional[Image.Image] = None,
            lab_image: Optional[np.ndarray] = None,
            image_url: Optional[HttpUrl] = None,
            grayscale_image: Optional[Image.Image] = None,
            png_image: Optional[BytesIO] = None,
            jpeg_image: Optional[BytesIO] = None,
            segments: Optional[Dict[str, Any]] = None,
            dom_analysis_result: Optional[Dict[str, Any]] = None,
    ) -> Optional[List[Union[int, str, float, Image.Image]]]:

        return [
            png_image.tell()
        ]
