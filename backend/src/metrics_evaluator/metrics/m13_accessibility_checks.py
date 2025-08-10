#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Metric: Accessibility checks by aXe

Description: Automated analyzis of web page content for accessibility testing.
The output is a JSON file that lists any accessibility violations found.

References:
     [1] T. Frazāo and C. Duarte (2020). Comparing accessibility evaluation plug-ins.
     W4A '20: Proceedings of the 17th International Web for All Conference, article no. 20, pp. 1-11.
     DOI: https://doi.org/10.1145/3371300.3383346

     [2] axe-selenium-python. URL: https://github.com/mozilla-services/axe-selenium-python

"""
import json
from io import BytesIO
from typing import Optional, Dict, Any, Union, List

import numpy as np
from PIL import Image

from axe_selenium_python import Axe
from commons.create_webdriver import create_webdriver
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
        with create_webdriver('') as driver:
            driver.get(image_url)
            axe = Axe(driver)
            # Inject axe-core javascript into page.
            axe.inject()
            # Run axe accessibility checks.
            results = axe.run()

        return [
            json.dumps(results["violations"]),
            len(results["violations"])
        ]



