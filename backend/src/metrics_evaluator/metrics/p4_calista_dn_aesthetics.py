#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Metric: Website Aesthetics Evaluation by Calista

Description: A comparison-based deep learning system which automatically assess website aesthetics.

References:
     [1] A. Delitzas, K. C. Chatzidimitriou, and A. L. Symeonidis (2023).
     Calista: A deep learning-based system for understanding and evaluating website aesthetics.
     International Journal of Human-Computer Studies, vol. 175, July 2023, 103019.
     DOI: https://doi.org/10.1016/j.ijhcs.2023.103019

"""
import json
from io import BytesIO
from typing import Optional, Dict, Any, Union, List

import numpy as np
import cv2
from PIL import Image

from metrics_evaluator.metrics.metric_interface import MetricInterface
from pydantic import HttpUrl

from keras.preprocessing.image import ImageDataGenerator
from keras.models import load_model
from commons.calista_utils import LRN, rmse, euclidean_distance_loss


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
        model = load_model('../calista_comparison_based.h5',
                           custom_objects={
                               'LRN': LRN,
                               'euclidean_distance_loss': euclidean_distance_loss,
                               'rmse': rmse
                           })
        print("model loaded")

        # prepare image array
        image_arr = []
        image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        resized_image = cv2.resize(image, (256, 192), interpolation=cv2.INTER_AREA)

        # Append the processed image to the list
        image_arr.append(resized_image)

        test_datagen = ImageDataGenerator(rescale = 1./255)
        test_data = test_datagen.flow(image_arr, batch_size=1, shuffle=False).next()

        score = model.predict(test_data)
        score = float(score)
        score = np.minimum(score, 10.0)
        score = np.maximum(score, 1.0)

        return [
            score
        ]





