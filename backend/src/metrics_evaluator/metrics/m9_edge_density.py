#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Metric: Edge density

Description: The percentage of pixels that are edge pixels, obtained through applying the canny edge detector to the
grayscale image.

References:
    [1] M. L. Mack and A. Oliva (2004). Computational estimation of visual complexity.
    12th Annual Object, Perception, Attention, and Memory Conference. Minneapolis, Minnesota.
    URL: https://scholar.google.com/citations?view_op=view_citation&hl=en&user=9bZsr-gAAAAJ&citation_for_view=9bZsr-gAAAAJ:4TOpqqG69KYC"

    [2] R. Rosenholtz, Y. Li, and L. Nakano (2007). Measuring Visual Clutter.
    Journal of Vision August 2007, vol. 7, 17, pp. 1-22.",
    DOI: "https://doi.org/10.1167/7.2.17"
"""

from io import BytesIO
from typing import Optional, Dict, Any, Union, List

from PIL import Image
import numpy as np

from metrics_evaluator.metrics.metric_interface import MetricInterface
from pydantic import HttpUrl
from skimage import feature


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

        # the sigma, low threshold, and high threshold values follow the values used by Rosenholtz et al.
        edges = feature.canny(np.array(grayscale_image), sigma=1.0, low_threshold=0.11, high_threshold=0.37)

        edge_density = np.sum(edges) / edges.size

        # Convert the edges array back to a PIL image
        edges_image = Image.fromarray((edges * 255).astype(np.uint8))

        # convert the PIL edge image to PNG
        buf = BytesIO()

        edges_image.save(buf, format="PNG")

        return [
            ("%.5f" % edge_density),
            buf
        ]



