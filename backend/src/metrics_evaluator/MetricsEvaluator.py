from pathos.multiprocessing import ProcessPool
from metrics_evaluator.ResultStorer import ResultStorer


class MetricsEvaluator:
    def __init__(self, wui_id, metric_modules, pil_image, lab_image, image_url, grayscale_image, png_image, jpeg_image, segments, dom_analysis_result):
        self.wui_id = wui_id
        self.metric_modules = metric_modules
        self.pil_image = pil_image
        self.lab_image = lab_image
        self.image_url = image_url
        self.grayscale_image = grayscale_image
        self.png_image = png_image
        self.jpeg_image = jpeg_image
        self.segments = segments
        self.dom_analysis_result = dom_analysis_result

    @staticmethod
    def extract_metric_id(module_name: str) -> str:
        prefix = "metrics_evaluator.metrics."
        # Remove the prefix
        if module_name.startswith(prefix):
            metric_name = module_name[len(prefix):]
        # Split by the first underscore and take the first part as the ID
        metric_id = metric_name.split('_', 1)[0]
        return metric_id

    def evaluate_metric(self, module):
        try:
            m = module.Metric()
            result = m.execute(
                pil_image=self.pil_image,
                lab_image=self.lab_image,
                image_url=self.image_url,
                grayscale_image=self.grayscale_image,
                png_image=self.png_image,
                jpeg_image=self.jpeg_image,
                segments=self.segments,
                dom_analysis_result=self.dom_analysis_result
            )
            metric_id = self.extract_metric_id(module.__name__)
            result_aggregator = ResultStorer(wui_id=self.wui_id, metric_id=metric_id, results=result)
            result_aggregator.store_result()
        except Exception as e:
            return module.__name__, str(e)

    def evaluate_metrics_parallel(self):
        with ProcessPool() as pool:
            [pool.apipe(self.evaluate_metric, module) for module in self.metric_modules]

    def evaluate_metrics_sequential(self):
        for module in self.metric_modules:
            self.evaluate_metric(module)
