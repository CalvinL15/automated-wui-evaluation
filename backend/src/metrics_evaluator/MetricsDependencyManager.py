from typing import List
from io import BytesIO
import re
from pathlib import Path
import importlib
import sys
from PIL import Image

from image_preprocessing.ImagePreprocessing import ImagePreprocessing
from metrics_evaluator.MetricsEvaluator import MetricsEvaluator

# constants for dynamic loading of metrics
METRICS_DIR: str = "metrics_evaluator/metrics"
METRICS_FILE_PATTERN: str = "*_*.py"

imagePreprocessing = ImagePreprocessing()


class MetricsDependencyManager:
    def __init__(self, wui_id: str, pil_image: Image.Image, png_image: BytesIO, metrics_to_evaluate: List[str], url, html_content, available_metrics):
        self.wui_id = wui_id
        self.pil_image = pil_image
        self.png_image = png_image
        self.metrics_to_evaluate = metrics_to_evaluate
        self.url = url
        self.html_content = html_content
        self.available_metrics = available_metrics

    async def identify_preprocessing_load_metrics_and_evaluate_metrics(self):
        metric_modules = []
        metric_modules_require_segmentation = []
        metric_modules_require_dom_analysis = []

        is_grayscale_conversion_required = False
        is_segmentation_required = False
        is_jpeg_conversion_required = False
        is_dom_analysis_required = False
        is_lab_conversion_required = False

        # Locate metric implementation and determine which preprocessing is required
        for metric in self.metrics_to_evaluate:
            metric_data = self.available_metrics["metrics"][metric]
            # determine which preprocessing is required
            if metric_data['preprocessing']['grayscale_conversion_required']:
                is_grayscale_conversion_required = True
            if metric_data['preprocessing']['segmentation_required']:
                is_segmentation_required = True
            if metric_data['preprocessing']['jpeg_conversion_required']:
                is_jpeg_conversion_required = True
            if metric_data['preprocessing']['dom_analysis_required']:
                is_dom_analysis_required = True
            if metric_data['preprocessing']['lab_conversion_required']:
                is_lab_conversion_required = True

            metric_files = [
                metric_file for metric_file in list(Path(METRICS_DIR).glob(METRICS_FILE_PATTERN))
                if metric_file.name.startswith(metric + "_")
            ]

            if metric_files:
                module_name = re.sub(r"/|\\", ".", str(metric_files[0].parent))
                metric_module_name = metric_files[0].stem  # 'stem' gives the filename without extension

                # Construct the full module import path
                full_module_name = f"{module_name}.{metric_module_name}"
                try:
                    if full_module_name in sys.modules:
                        metric_module = importlib.reload(sys.modules[full_module_name])
                    else:
                        metric_module = importlib.import_module(full_module_name)
                    if metric_data['preprocessing']['segmentation_required']:
                        metric_modules_require_segmentation.append(metric_module)
                    elif metric_data['preprocessing']['dom_analysis_required']:
                        metric_modules_require_dom_analysis.append(metric_module)
                    else:
                        metric_modules.append(metric_module)
                except ModuleNotFoundError as e:
                    print(f"Failed to import {full_module_name}: {e}")
            else:
                print('metric not found!')

        # initialize
        gui_segments = None
        grayscale_image = None
        jpeg_image = None
        dom_analysis_result = None
        lab_image = None

        if is_grayscale_conversion_required:
            grayscale_image = imagePreprocessing.convert_pil_image_to_grayscale(self.pil_image)

        if is_jpeg_conversion_required:
            jpeg_image = imagePreprocessing.convert_pil_image_to_jpeg(self.pil_image)

        if is_lab_conversion_required:
            lab_image = imagePreprocessing.convert_pil_image_to_lab(self.pil_image)

        metric_evaluator = MetricsEvaluator(
            wui_id=self.wui_id,
            metric_modules=metric_modules,
            pil_image=self.pil_image,
            lab_image=lab_image,
            image_url=self.url,
            grayscale_image=grayscale_image,
            png_image=self.png_image,
            jpeg_image=jpeg_image,
            segments=gui_segments,
            dom_analysis_result=dom_analysis_result
        )

        # evaluate metrics which do not require either dom_analysis_result nor segmentation
        metric_evaluator.evaluate_metrics_parallel()

        if is_dom_analysis_required:
            from dom_analyzer.DOMAnalyzer import DOMAnalyzer
            dom_analyzer = DOMAnalyzer(url=self.url, html=self.html_content)
            if self.url is not None:
                dom_analysis_result = dom_analyzer.analyze_url()
            else:
                dom_analysis_result = dom_analyzer.analyze_html()

        metric_evaluator_require_dom_analysis = MetricsEvaluator(
            wui_id=self.wui_id,
            metric_modules=metric_modules_require_dom_analysis,
            pil_image=self.pil_image,
            lab_image=lab_image,
            image_url=self.url,
            grayscale_image=grayscale_image,
            png_image=self.png_image,
            jpeg_image=jpeg_image,
            segments=gui_segments,
            dom_analysis_result=dom_analysis_result
        )

        # evaluate metrics which require dom_analysis_result, but not segmentation
        metric_evaluator_require_dom_analysis.evaluate_metrics_parallel()

        if is_segmentation_required:
            from image_preprocessing.segmentation.model import Segmentation
            gui_segments = Segmentation.execute(self.pil_image)

        metric_evaluator_require_segmentation = MetricsEvaluator(
            wui_id=self.wui_id,
            metric_modules=metric_modules_require_segmentation,
            pil_image=self.pil_image,
            lab_image=lab_image,
            image_url=self.url,
            grayscale_image=grayscale_image,
            png_image=self.png_image,
            jpeg_image=jpeg_image,
            segments=gui_segments,
            dom_analysis_result=dom_analysis_result
        )

        # metric_evaluator_require_segmentation.evaluate_metrics_parallel()
        metric_evaluator_require_segmentation.evaluate_metrics_parallel()

        # for performance testing, where f1, f2, and f3 are for the different MetricEvaluator classes
        # results = f1 + f2 + f3
        #
        # for result in results:
        #     result.get()




