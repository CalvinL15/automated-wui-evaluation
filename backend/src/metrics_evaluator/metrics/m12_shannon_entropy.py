#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Metric: Shannon's information entropy

Description: A measure of unpredictability and uncertainty of information in a set of data.
In the context of an image, the entropy quantifies the amount of information contained within the image.
The input will be evaluated as a grayscale image.

References:
    [1] E. Boychuk and M. Bakaev (2019). Entropy and Compression Based Analysis of Web User Interfaces.
    International Conference on Web Engineering (ICWE) 2019, pp. 253-261.
    DOI: https://doi.org/10.1007/978-3-030-19274-7_19
"""

from io import BytesIO
from typing import Optional, Dict, Any, Union, List

import numpy as np
from PIL import Image

from metrics_evaluator.metrics.metric_interface import MetricInterface
from pydantic import HttpUrl
from skimage.measure import shannon_entropy


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

        entropy = shannon_entropy(grayscale_image)

        return [
            entropy
        ]



