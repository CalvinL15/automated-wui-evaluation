#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Metric: UIED Segmentation

Description: GUI element segmentation and detection that integrates both traditional computer vision methods
and deep learning methods to achieve accurate detection.

References:

    [1] M. Xie, S. Feng, Z. Xing, J. Chen, and C. Chen (2020). UIED: A Hybrid Tool for GUI Element Detection.
    Proceedings of the 28th ACM Joint Meeting on European Software Engineering Conference and Symposium on the
    Foundations of Software Engineering, pp. 1655-1659.
    DOI: https://doi.org/10.1145/3368089.3417940

    [2] A. Oulasvirta, S. De Pascale, J. Koch, T. Langerak, J. Jokinen, K. Todi, M. Laine,
    M. Kristhombuge, Z. Yuxi, A. Miniukovich, G. Palmas, T. Weinkauf (2018).
    Aalto Interface Metrics (AIM): A Service and Codebase for Computational GUI Evaluation.
    Adjunct Proceedings of the 31st Annual ACM Symposium on User Interface Software and Technology, pp. 16-19.
    DOI: https://doi.org/10.1145/3266037.3266087
"""

from io import BytesIO
from typing import Optional, Any, Dict, Union, List

import numpy as np
from PIL import Image
from pydantic import HttpUrl

from metrics_evaluator.metrics.metric_interface import MetricInterface


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

        # Get all elements
        if segments is not None:
            segmented_im: BytesIO = segments["img_bytes_io"]
        else:
            raise ValueError("The value of 'segments' cannot be 'None'.")

        # delete image bytes from the list
        del segments["img_bytes_io"]

        return [
            segmented_im,
            segments
        ]

