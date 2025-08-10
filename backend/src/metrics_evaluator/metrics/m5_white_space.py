#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Metric: White space

Description: The proportion of white space in the UI.

References:

    [1] A. Miniukovich and A. De Angeli (2015). Computation of Interface Aesthetics.
    CHI'15: Proceedings of the 33rd Annual ACM Conference on Human Factor in Computing Systems, pp. 1163-1172.
    DOI: https://doi.org/10.1145/2702123.2702575

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

        if segments is not None:
            # Create a binary array (default = 1) with the same size of image
            height, width, _ = segments["img_shape"]
            segments: List = segments["segments"]
            img_binary = np.ones((height, width), dtype=int)

            # Fill the binary array with 0 for the elements
            for element in segments:
                position = element["position"]
                img_binary[position["row_min"]: position["row_max"], position["column_min"]: position["column_max"], ] \
                    = 0

            # Compute white space (percentage)
            white_space: float = float(np.mean(img_binary))
        else:
            raise ValueError("The value of 'segments' cannot be 'None'.")

        return [
            white_space
        ]
