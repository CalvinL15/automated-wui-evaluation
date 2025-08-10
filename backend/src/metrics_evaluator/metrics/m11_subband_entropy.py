#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Metric: Subband entropy

Description: A measure of clutter based on measure of the efficiency with which
the image can be encoded while maintaining perceptual image quality.

References:
    [1] R. Rosenholtz, Y. Li, and L. Nakano (2007). Measuring Visual Clutter.
    Journal of Vision August 2007, vol. 7, 17, pp. 1-22.",
    DOI: "https://doi.org/10.1167/7.2.17"

    [2] A. Miniukovich and A. De Angeli (2015). Computation of Interface Aesthetics.
    CHI'15: Proceedings of the 33rd Annual ACM Conference on Human Factor in Computing Systems, pp. 1163-1172.
    DOI: https://doi.org/10.1145/2702123.2702575

    [3] A. Oulasvirta, S. De Pascale, J. Koch, T. Langerak, J. Jokinen, K. Todi, M. Laine,
    M. Kristhombuge, Z. Yuxi, A. Miniukovich, G. Palmas, T. Weinkauf (2018).
    Aalto Interface Metrics (AIM): A Service and Codebase for Computational GUI Evaluation.
    Adjunct Proceedings of the 31st Annual ACM Symposium on User Interface Software and Technology, pp. 16-19.
    DOI: https://doi.org/10.1145/3266037.3266087

"""

from io import BytesIO
from typing import Optional, Dict, Any, Union, List

import numpy as np
from PIL import Image

from metrics_evaluator.metrics.metric_interface import MetricInterface
from commons.visual_clutter_utils import entropy
from pydantic import HttpUrl
from pyrtools import pyramids


class Metric(MetricInterface):
    """
        Mostly based on the AIM's python implementation on the metric (available at: https://github.com/aalto-ui/aim),
        which is based on the MATLAB implementation by Rosenholtz et al, available at: http://hdl.handle.net/1721.1/37593
    """

    # private constants
    _SCALES: int = 3  # the number of spatial scales for the subband decomposition
    _WGHT_CHROM: float = 0.0625  # the weight on chrominance
    _ORIENTATION: int = 4  # the number of orientations for the subband decomposition
    _ZERO_THRESHOLD: float = 0.008  # threshold to consider an array as a zeros array

    @classmethod
    def _band_entropy(cls, image_map):
        # Decompose the image into subbands
        SFpyr = pyramids.SteerablePyramidFreq(
            image_map, height=cls._SCALES, order=cls._ORIENTATION - 1
        )

        S = SFpyr.pyr_coeffs

        en_band = []
        for ind in S.keys():
            en_band.append(entropy(S[ind].ravel()))

        return en_band

    @classmethod
    def execute(
            cls,
            pil_image: Optional[Image.Image] = None,
            lab_image: Optional[np.ndarray] = None,
            image_url: Optional[HttpUrl] = None,
            grayscale_image: Optional[Image.Image] = None,
            png_image: Optional[BytesIO] = None,
            jpeg_image: Optional[BytesIO] = None,
            segments: Optional[Dict[str, Any]] = None,
            dom_analysis_result: Optional[Dict[str, Any]] = None,
    ) -> Optional[List[Union[int, str, float, Image.Image]]]:

        # Split image to the luminance (lum) and chrominance (a,b) channels
        lum = lab_image[:, :, 0]
        a = lab_image[:, :, 1]
        b = lab_image[:, :, 2]

        # Compute subband entropy for the luminance channel
        en_band = cls._band_entropy(lum)
        clutter_se = float(np.mean(en_band))

        # Compute subband entropy for the chrominance channels
        for jj in [a, b]:
            if np.max(jj) - np.min(jj) < cls._ZERO_THRESHOLD:
                jj = np.zeros_like(jj)

            en_band = cls._band_entropy(jj)
            clutter_se = float(clutter_se + cls._WGHT_CHROM * np.mean(en_band))

        clutter_se = clutter_se / (1 + 2 * cls._WGHT_CHROM)

        return [
            clutter_se
        ]
