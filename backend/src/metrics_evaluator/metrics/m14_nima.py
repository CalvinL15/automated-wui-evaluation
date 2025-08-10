#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Metric: NIMA (Neural IMage Assessment)


Description: The predicted technical and aesthetic qualities of images.


Source: Model is available: https://github.com/delldu/ImageNima/tree/master/models

References:
    [1] H. Talebi and P. Milanfar (2018). NIMA: Neural Image Assessment.
        IEEE Transactions on Image Processing, 27(8), 3998-4011.
        DOI: https://doi.org/10.1109/TIP.2018.2831899

    [2] A. Oulasvirta, S. De Pascale, J. Koch, T. Langerak, J. Jokinen, K. Todi, M. Laine,
        M. Kristhombuge, Z. Yuxi, A. Miniukovich, G. Palmas, T. Weinkauf (2018).
        Aalto Interface Metrics (AIM): A Service and Codebase for Computational GUI Evaluation.
        Adjunct Proceedings of the 31st Annual ACM Symposium on User Interface Software and Technology, pp. 16-19.
        DOI: https://doi.org/10.1145/3266037.3266087
"""


# Standard library modules
import collections
from pathlib import Path
from io import BytesIO
from typing import Optional, Dict, Any, Union, List

import numpy as np
from pydantic import HttpUrl
from PIL import Image

import torch
import torch.nn as nn
from torchvision import models, transforms


from metrics_evaluator.metrics.metric_interface import MetricInterface


class Metric(MetricInterface):
    # The original model can be downloaded from here: https://github.com/delldu/ImageNima/tree/master/models
    _MODEL_PATH: Path = Path(
        "./metrics_evaluator/dense121_all.pt"
    )

    _DEVICE = torch.device("cpu")

    # Define DenseNet121 model
    _NUM_CLASS: int = 10
    _INPUT_SIZE: int = 224
    _MODEL: models.densenet.DenseNet = models.densenet121(pretrained=False)
    _NUM_FTRS: int = _MODEL.classifier.in_features
    _MODEL.classifier = nn.Sequential(
        nn.Linear(_NUM_FTRS, _NUM_CLASS), nn.Softmax(1)
    )

    # Load state dict: weights
    _STATE_DICT: collections.OrderedDict = torch.load(
        _MODEL_PATH, map_location=lambda storage, loc: storage
    )

    _MODEL.load_state_dict(_STATE_DICT)
    _MODEL = _MODEL.to(_DEVICE)
    _MODEL.eval()

    # Transform method: Since the trained model only works with square
    # photos, the input image needs to be resized.
    # The implemented transformer returns the center square
    # of the resized input image (smaller edge is 224, without changing
    # ratio), which is one of the most popular transformers for non-square
    # images.

    _transform: transforms.transforms.Compose = transforms.Compose(
        [transforms.Resize(_INPUT_SIZE), transforms.CenterCrop(_INPUT_SIZE), transforms.ToTensor()]
    )

    # Public methods
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
    ) -> Optional[List[Union[int, float, str]]]:

        # Compute votes and send to device
        weighted_votes: torch.Tensor = (
                torch.arange(cls._NUM_CLASS, dtype=torch.float) + 1
        )
        weighted_votes = weighted_votes.to(cls._DEVICE)

        # Resize image to fit network input
        img_resized: torch.Tensor = cls._transform(pil_image)
        img_resized = img_resized.to(cls._DEVICE)

        # Predict
        with torch.no_grad():
            scores: torch.Tensor = cls._MODEL(
                img_resized.view(1, 3, cls._INPUT_SIZE, cls._INPUT_SIZE)
            )
            mean: torch.Tensor = torch.matmul(scores, weighted_votes)
            std: torch.Tensor = torch.sqrt(
                (
                        scores * torch.pow((weighted_votes - mean.view(-1, 1)), 2)
                ).sum(dim=1)
            )

        # Compute metrics
        nima_mean_score: float = float(mean)
        nima_std_score: float = float(std)

        return [
            nima_mean_score,
            nima_std_score,
        ]
