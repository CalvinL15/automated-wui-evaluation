#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Metric: Colorfulness by Hassler & Süsstrunk

Description: Quantification of colorfulness in natural images, ignoring hue.

References:
    [1] D. Hasler and S. Süsstrunk (2003). Measuring Colorfulness in Natural Images.
    Proceedings of IS&T/SPIE Electronic Image 2003: Human Vision and Electronic Imaging VIII, pp. 87-95.
    DOI: https://doi.org/10.1117/12.477378

    [2] K. Reinecke, T. Yeh, L. Miratrix, R. Mardiko, Y. Zhao, J. Liu, and K. Z. Gajos (2013).
    Predicting User' First Impression of Website Aesthetics with Quantification of Perceived Visual Complexity and Colorfulness.
    Proceedings of the SIGCHI Conference on Human Factors in Computing Systems, pp. 2049-2058.
    DOI: "https://doi.org/10.1145/2470654.2481281"
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

        colorfulness_coefficient = 0.3
        np_image_float = np.array(pil_image).astype(float)

        # extract RGB channels
        red = np_image_float[:, :, 0]
        green = np_image_float[:, :, 1]
        blue = np_image_float[:, :, 2]

        # compute red-green and yellow-blue (defined in chapter 7 of the paper by Hasler & Süsstrunk)
        rg = red - green
        yb = 0.5 * (red + green) - blue

        # compute metrics based on Hassler and Süsstrunk's paper
        rgyb_avg: float = float(np.sqrt(np.mean(rg) ** 2 + np.mean(yb) ** 2))
        rgyb_std: float = float(np.sqrt(np.std(rg) ** 2 + np.std(yb) ** 2))
        colorfulness: float = float(rgyb_std + colorfulness_coefficient * rgyb_avg)

        return [
            colorfulness
        ]