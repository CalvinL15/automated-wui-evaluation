#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Metric: Word count

Description: Total words of the page.

References:
    [1] M. Y. Ivory, R. R. Sinha and M. A. Hearst (2001). Empirically Validated Web Page Design Metrics.
    Proceedings of the SIGCHI Conference on Human Factors in Computing Systems (CHI '01), pp. 53-60.
    DOI: https://doi.org/10.1145/365024.365035"
"""
from io import BytesIO
from typing import Optional, Dict, Any, Union, List
import re

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

        # reference for the used regex to find all words:
        # https://stackoverflow.com/questions/14138199/python-regex-find-all-words-in-text

        return [
            len(re.findall(r'\b\S+\b', dom_analysis_result['text']))
        ]
