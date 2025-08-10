#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Metric: UMSI (Unified Model of Saliency and Importance)

Description: Prediction of human attention on various design classes and natural images, visualized through a heatmap
that represent importance values, along with the original image overlaid by the heatmap.

References:

    [1] C. Fosco, V. Casser, A. K. Bedi, P. O'Donovan, A. Hertzmann, and Z. Bylinskii (2020).
    Predicting Visual Importance Across Graphic Design Types.
    Proceedings of the 33rd Annual ACM Symposium on User Interface Software and Technology, pp. 249-260.
    DOI: https://doi.org/10.1145/3379337.3415825
"""
from pathlib import Path
import gc
from io import BytesIO
from typing import Optional, Any, Dict, Union, List

import numpy as np
import scipy
import skimage.transform as skit
from PIL import Image
from matplotlib import pyplot as plt, cm
from pydantic import HttpUrl

from metrics_evaluator.metrics.metric_interface import MetricInterface
import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.python.keras import backend as K

class Metric(MetricInterface):
    """
        Reference:
        Based on Fosco et al.'s implementation available at https://github.com/diviz-mit/predimportance-public
        """

    # Private constants
    _SHAPE_R: int = 240  # input shape (rows) of the model
    _SHAPE_C: int = 320  # input shape (columns) of the model
    _SHOW: bool = False
    _HEATMAP_STYLE: str = "viridis"

    @classmethod
    def _padding(cls, img, channels=3) -> np.ndarray:
        img_padded: np.ndarray = np.zeros((cls._SHAPE_R, cls._SHAPE_C, channels), dtype=np.uint8)
        if channels == 1:
            img_padded = np.zeros((cls._SHAPE_R, cls._SHAPE_C), dtype=np.uint8)

        original_shape = np.asarray(img).shape
        rows_rate = original_shape[0] / cls._SHAPE_R
        cols_rate = original_shape[1] / cls._SHAPE_C

        if rows_rate > cols_rate:
            new_cols = (original_shape[1] * cls._SHAPE_R) // original_shape[0]
            img = img.resize((new_cols, cls._SHAPE_R))
            if new_cols > cls._SHAPE_C:
                new_cols = cls._SHAPE_C
            img_padded[:,
            ((img_padded.shape[1] - new_cols) // 2):((img_padded.shape[1] - new_cols) // 2 + new_cols)] = img
        else:
            new_rows = (original_shape[0] * cls._SHAPE_C) // original_shape[1]
            img = img.resize((cls._SHAPE_C, new_rows))
            if new_rows > cls._SHAPE_R:
                new_rows = cls._SHAPE_R
            img_padded[((img_padded.shape[0] - new_rows) // 2):((img_padded.shape[0] - new_rows) // 2 + new_rows),
            :] = img

        return img_padded

    @classmethod
    def _preprocess_images(cls, images: List[Image.Image], show=False) -> np.ndarray:

        ims: np.ndarray = np.zeros(
            (len(images), cls._SHAPE_R, cls._SHAPE_C, 3)
        )

        for i, original_image in enumerate(images):
            img: Union[np.ndarray, Image.Image] = original_image

            padded_image = cls._padding(img, 3)
            ims[i] = padded_image

            if show:
                plt.figure(figsize=[8, 8])
                plt.subplot(1, 2, 1)
                plt.imshow(original_image)
                plt.title("Original image")
                plt.subplot(1, 2, 2)
                plt.imshow(padded_image)
                plt.title("Input to network")
                plt.show()

        ims[:, :, :, 0] -= 103.939
        ims[:, :, :, 1] -= 116.779
        ims[:, :, :, 2] -= 123.68

        return ims

    @classmethod
    def _postprocess_predictions(cls, img, pred, blur: bool = False, normalize: bool = False) -> np.ndarray:
        predictions_shape = pred.shape
        width, height = img.size
        rows_rate = height / predictions_shape[0]
        cols_rate = width / predictions_shape[1]

        if blur:
            sigma = blur
            pred = scipy.ndimage.filters.gaussian_filter(pred, sigma=sigma)

        image: np.ndarray

        if rows_rate > cols_rate:
            new_cols = (predictions_shape[1] * height) // predictions_shape[0]
            pred = skit.resize(pred, (height, new_cols))
            image = pred[:, ((pred.shape[1] - width) // 2):((pred.shape[1] - width) // 2 + width)]
        else:
            new_rows = (predictions_shape[0] * width) // predictions_shape[1]
            pred = skit.resize(pred, (new_rows, width))
            image = pred[((pred.shape[0] - height) // 2):((pred.shape[0] - height) // 2 + height), :]

        if normalize:
            image = img / np.max(img) * 255

        return image

    @classmethod
    def _heatmap_overlay(cls, im: Image.Image, heatmap: np.ndarray, colmap: str = 'hot') -> np.ndarray:
        cm_array = cm.get_cmap(colmap)
        im_array = np.asarray(im)
        heatmap_norm = (heatmap - np.min(heatmap)) / float(np.max(heatmap) - np.min(heatmap))
        heatmap_hot = cm_array(heatmap_norm)
        res_final = im_array.copy()
        heatmap_rep = np.repeat(heatmap_norm[:, :, np.newaxis], 3, axis=2)
        res_final[...] = heatmap_hot[..., 0:3] * 255.0 * heatmap_rep + im_array[...] * (1 - heatmap_rep)
        return res_final

    @classmethod
    def _show_result(
            cls,
            original_image: Image.Image,
            heatmap: np.ndarray,
            heatmap_overlay: np.ndarray
    ) -> None:
        plt.figure(figsize=[15, 7])
        plt.subplot(1, 3, 1)
        plt.imshow(original_image)
        plt.title("Original image")
        plt.subplot(1, 3, 2)
        plt.imshow(heatmap)
        plt.title("Prediction heatmap")
        plt.subplot(1, 3, 3)
        plt.imshow(heatmap_overlay)
        plt.title("Prediction heatmap overlay")
        plt.show()

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

        # adjust parallelism of tensorflow
        tf.config.threading.set_inter_op_parallelism_threads(1)
        tf.config.threading.set_intra_op_parallelism_threads(1)

        original_images: List[Image.Image] = [pil_image]
        # Preprocess images
        preprocessed_ims: np.ndarray = cls._preprocess_images(images=original_images, show=cls._SHOW)

        # Load model, the original model can be downloaded from here:
        # http://predimportance.mit.edu/data/xception_cl_fus_aspp_imp1k_10kl-3cc0.1mse-5nss5bc_bs4_ep30_valloss-2.5774_full.h5

        model_filepath: Path = Path(
            "./metrics_evaluator/xception_model"
        )

        model: keras.engine.training.Model = keras.models.load_model(model_filepath, custom_objects={"K": K}, compile=False)

        # Predict maps
        preds: List[np.ndarray] = model.predict(preprocessed_ims)

        # Postprocess predictions to get it back to the original size
        heatmap: np.ndarray = cls._postprocess_predictions(img=original_images[0], pred=preds[0][0, :, :, 0])

        # Create prediction heatmap overlay
        heatmap_overlay: np.ndarray = cls._heatmap_overlay(
            im=original_images[0], heatmap=heatmap, colmap=cls._HEATMAP_STYLE
        )

        # Show result
        if cls._SHOW:
            cls._show_result(original_images[0], heatmap, heatmap_overlay)

        # Prepare final results
        img_umsi_prediction_heatmap: Image.Image = Image.fromarray(
            # Apply the color map, rescale to the 0-255 range, convert to
            # 8-bit unsigned integers. Note: Slight loss of accuracy due
            # the float32 to uint8 conversion.
            (cm.get_cmap("viridis")(heatmap) * 255).astype("uint8")
        ).convert("RGB")
        img_umsi_prediction_heatmap_overlay: Image.Image = Image.fromarray(heatmap_overlay).convert("RGB")

        umsi_prediction_heatmap: BytesIO = BytesIO()
        img_umsi_prediction_heatmap.save(umsi_prediction_heatmap, format="PNG")

        umsi_prediction_heatmap_overlay: BytesIO = BytesIO()
        img_umsi_prediction_heatmap_overlay.save(umsi_prediction_heatmap_overlay, format="PNG")

        # Clean up to prevent Keras memory leaks
        del model
        K.clear_session()
        _ = gc.collect()

        # uncomment the next two lines to see the images
        # img_umsi_prediction_heatmap.show()
        # img_umsi_prediction_heatmap_overlay.show()

        return [
            umsi_prediction_heatmap,
            umsi_prediction_heatmap_overlay
        ]
