#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Metric: CIELAB Color Average and Standard Deviation

Description: CIELAB is a color space that expresses color as three values: L* for lightness and a* and b* for the green–red and blue–yellow color components.

References:

    [1] D. Hasler and S. Süsstrunk (2003). Measuring Colorfulness in Natural Images.
    Proceedings of IS&T/SPIE Electronic Image 2003: Human Vision and Electronic Imaging VIII, pp. 87-95.
    DOI: https://doi.org/10.1117/12.477378

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

        # get LAB
        L: np.ndarray = lab_image[:, :, 0]
        A: np.ndarray = lab_image[:, :, 1]
        B: np.ndarray = lab_image[:, :, 2]

        # Compute average and standard deviation for each value separately
        L_avg: float = float(np.mean(L))
        L_std: float = float(np.std(L))
        A_avg: float = float(np.mean(A))
        A_std: float = float(np.std(A))
        B_avg: float = float(np.mean(B))
        B_std: float = float(np.std(B))

        return [
            L_avg,
            L_std,
            A_avg,
            A_std,
            B_avg,
            B_std,
        ]