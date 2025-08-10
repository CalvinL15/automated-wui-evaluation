#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
from io import BytesIO
from typing import Any, Dict, List, Optional, Union

import numpy as np
from PIL import Image
from pydantic import HttpUrl


class MetricInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
                hasattr(subclass, "execute")
                and callable(subclass.execute)
                or NotImplemented
        )

    # Abstract methods
    @abc.abstractmethod
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
        """
        Execute the metric.

        Args:
            pil_image: the image in PIL image object with PNG format (RGB)
            lab_image: a NumPy array representing an image in the CIELAB color space.
            image_url: the URL of which the screenshot of the input is taken
            grayscale_image: the image in grayscale in PIL image object
            png_image: BytesIO object containing the PNG image representation of the input
            jpeg_image: BytesIO object containing the JPEG image representation of the input
            segments: the image segments based on the UIED segmentation method
            dom_analysis_result: the result of the DOM analysis for the input

        Returns:
            Results (list of measures)

        Raises:
            NotImplementedError: Implementation is missing
        """
        raise NotImplementedError
