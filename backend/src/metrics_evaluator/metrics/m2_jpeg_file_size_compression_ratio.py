#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Metric: JPEG file size and compression ratio (100)

Description: Analysis of an image converted to JPEG format with 100% quality, providing both the JPEG file size in bytes and the compression ratio.

References:
    [1] R. Rosenholtz, Y. Li, and L. Nakano (2007). Measuring Visual Clutter.
    Journal of Vision August 2007, vol. 7, 17, pp. 1-22.,
    DOI: https://doi.org/10.1167/7.2.17

    [2] A. Miniukovich and A. De Angeli (2015). Computation of Interface Aesthetics.
    CHI'15: Proceedings of the 33rd Annual ACM Conference on Human Factor in Computing Systems, pp. 1163-1172.
    DOI: https://doi.org/10.1145/2702123.2702575

    [3] E. Boychuk and M. Bakaev (2019). Entropy and Compression Based Analysis of Web User Interfaces.
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

        img_file_size_png = png_image.tell()
        img_file_size_jpeg = jpeg_image.tell()

        return [
            img_file_size_jpeg,
            img_file_size_png / img_file_size_jpeg
        ]