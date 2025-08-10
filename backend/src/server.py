from enum import Enum
from io import BytesIO
from typing import List, Optional, Dict, Union
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from image_preprocessing.ImagePreprocessing import ImagePreprocessing
from screenshot_capturer.ScreenshotCapturer import ScreenshotCapturer
from metrics_evaluator.MetricsDependencyManager import MetricsDependencyManager
import db_client
from email_utils import send_email, create_email_content
from metric_extension_utils import process_approved_metric

import os
import json
import tempfile
import zipfile

from PIL import Image
from dotenv import load_dotenv

# load env
load_dotenv()

# constants for dynamic loading of metrics
METRICS_DIR: str = "metrics_evaluator/metrics"
METRICS_FILE_PATTERN: str = "*_*.py"

app = FastAPI()
imagePreprocessing = ImagePreprocessing()
capturer = ScreenshotCapturer()

available_metrics = {}

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AcceptedInput(str, Enum):
    html = 'html'
    url = 'url'
    png = 'png'


class ResultType(str, Enum):
    text = 'text'
    json = 'json'
    image = 'image'


class Reference(BaseModel):
    title: str
    url: HttpUrl


class ScoreRange(BaseModel):
    range: List[Optional[float]]  # Allows None values in the range list to represent open-ended ranges
    description: Union[str, bool]


class Result(BaseModel):
    name: str
    description: str
    type: ResultType
    scores: Optional[List[ScoreRange]] = None  # Scores is an optional field


class Preprocessing(BaseModel):
    grayscale_conversion_required: bool
    jpeg_conversion_required: bool
    segmentation_required: bool
    dom_analysis_required: bool
    lab_conversion_required: bool


class Metric(BaseModel):
    name: str
    accepted_input: List[AcceptedInput]
    description: str
    preprocessing: Preprocessing
    references: Optional[List[Reference]]
    results: List[Result]


class Metrics(BaseModel):
    metrics: Dict[str, Metric]


class UrlInput(BaseModel):
    url: str
    metrics: List[str]


class FileInput(BaseModel):
    file: UploadFile
    metrics: List[str]


class MetricKeys(BaseModel):
    metrics: List[str]


# Load metrics.json
with open('../metrics.json', 'r') as metrics_json:
    available_metrics = json.load(metrics_json)


@app.on_event("startup")
async def check_approved_metrics():
    config_data = {}
    approved_metrics = db_client.get_approved_metrics()
    for metric in approved_metrics:
        config_data.update(await process_approved_metric(metric))
    available_metrics["metrics"].update(config_data)


# retrieve all available metrics
@app.get('/api/metrics', summary="List all available metrics",
         description="Retrieve a list of all available metrics with their details.")
async def get_metrics() -> Metrics:
    await check_approved_metrics()
    return available_metrics


# Retrieve a specific metric by ID
@app.get('/api/metrics/{metric_id}', summary="Get a specific metric",
         description="Retrieve detailed information about a specific metric by its ID.")
def get_metric(metric_id: str) -> Metric:
    metric: Metric = available_metrics['metrics'].get(metric_id)
    if metric is None:
        raise HTTPException(status_code=404, detail="Metric not found")
    return metric


class EvaluateInputReturnType(BaseModel):
    wui_name: str
    result_id: str
    wui_type: str


@app.post('/api/evaluate_url_input', summary="Evaluate WUI (URL string)", description="Evaluate WUI in a form of file (binary data). Accepts text/html or image/png")
async def evaluate_url_input(url_input: UrlInput, background_tasks: BackgroundTasks) -> EvaluateInputReturnType:
    with capturer.capture_screenshot_url(url=url_input.url) as screenshot_image:
        png_image = imagePreprocessing.convert_pil_image_to_png(image=screenshot_image)
    # upload screenshot image and retrieve its public URL
    screenshot_url = db_client.upload_file(
        file=png_image,
        file_extension=".png"
    )

    # upload file metadata to PostGreSQL DB
    data = db_client.insert_file_metadata(
        wui_name=url_input.url,
        screenshot_url=screenshot_url,
        html_url=None,
        metrics_to_evaluate=url_input.metrics
    )

    metrics = await get_metrics()

    metricsEvaluatorHandler = MetricsDependencyManager(
        wui_id=data['id'],
        pil_image=screenshot_image,
        png_image=png_image,
        metrics_to_evaluate=url_input.metrics,
        url=url_input.url,
        html_content=None,
        available_metrics=metrics
    )

    # uncomment for system performance test
    # await metricsEvaluatorHandler.identify_preprocessing_load_metrics_and_evaluate_metrics()

    # comment for system performance test
    background_tasks.add_task(
        metricsEvaluatorHandler.identify_preprocessing_load_metrics_and_evaluate_metrics
    )

    # return the input name as well as result_id which will be used to construct the unique URL for the result page
    return {
        "wui_name": data['wui_name'],
        "result_id": str(data['id']),
        "wui_type": "url"
    }


@app.post('/api/evaluate_file_input', summary="Evaluate WUI (HTML, ZIP or PNG format type)", description="Evaluate WUI in a form of a uploaded file")
async def evaluate_file_input(background_tasks: BackgroundTasks, file: UploadFile = File(...), metrics: str = Form(...)) -> EvaluateInputReturnType:
    metrics_dict = json.loads(metrics)  # Deserialize JSON string to Python dict
    metrics_data = MetricKeys(**metrics_dict)  # Convert dict to Pydantic model
    if file.content_type == 'application/zip':
        wui_type = "zip"
        # Create a temporary directory to extract the zip file
        temp_dir = f"/tmp/{file.filename}"
        os.makedirs(temp_dir, exist_ok=True)

        # Extract the zip file
        with zipfile.ZipFile(BytesIO(await file.read()), 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Identify the index.html file
        index_html_path = os.path.join(temp_dir, 'index.html')
        if not os.path.exists(index_html_path):
            raise HTTPException(status_code=400, detail="index.html not found in the ZIP file")

        # Read the HTML content
        with open(index_html_path, 'r') as f:
            html_content = f.read()

        # Render the HTML content and capture a screenshot
        screenshot_image = capturer.capture_screenshot_html(html_path=index_html_path)
        png_image = imagePreprocessing.convert_pil_image_to_png(image=screenshot_image)

        # Upload screenshot image and retrieve its public URL
        image_url = db_client.upload_file(file=png_image, file_extension=".png")

        # Upload HTML file and retrieve its public URL
        with open(index_html_path, 'rb') as f:
            html_bytes = f.read()
        html_url = db_client.upload_file(file=BytesIO(html_bytes), file_extension=".html", content_type='text/html')

        # Upload file metadata to PostGreSQL DB
        data = db_client.insert_file_metadata(
            wui_name=file.filename,
            screenshot_url=image_url,
            html_url=html_url,
            metrics_to_evaluate=metrics_data.metrics
        )

        metrics = await get_metrics()

        metricsEvaluatorHandler = MetricsDependencyManager(
            wui_id=data['id'],
            pil_image=screenshot_image,
            png_image=png_image,
            metrics_to_evaluate=metrics_data.metrics,
            url=None,
            html_content=html_content,
            available_metrics=metrics
        )

        # Add a background task (evaluating the metrics) to run after the response is sent
        background_tasks.add_task(
            metricsEvaluatorHandler.identify_preprocessing_load_metrics_and_evaluate_metrics
        )

    elif file.content_type == 'text/html':  # require screenshot to be captured
        wui_type = "html"
        html_content = await file.read()

        # Create a temporary file to save the HTML content
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
            tmp.write(html_content)
            tmp_html_path = tmp.name

        screenshot_image = capturer.capture_screenshot_html(html_path=tmp_html_path)
        png_image = imagePreprocessing.convert_pil_image_to_png(image=screenshot_image)

        # upload screenshot image and retrieve its public URL
        image_url = db_client.upload_file(file=png_image, file_extension=".png")
        # upload html file and retrieve its public URL
        html_url = db_client.upload_file(file=file.file, file_extension=".html", content_type='text/html')

        # upload file metadata to PostGreSQL DB
        data = db_client.insert_file_metadata(
            wui_name=file.filename,
            screenshot_url=image_url,
            html_url=html_url,
            metrics_to_evaluate=metrics_data.metrics
        )

        metrics = await get_metrics()

        metricsEvaluatorHandler = MetricsDependencyManager(
            wui_id=data['id'],
            pil_image=screenshot_image,
            png_image=png_image,
            metrics_to_evaluate=metrics_data.metrics,
            url=None,
            html_content=html_content,
            available_metrics=metrics
        )

        # Add a background task (evaluating the metrics) to run after the response is sent
        background_tasks.add_task(
            metricsEvaluatorHandler.identify_preprocessing_load_metrics_and_evaluate_metrics
        )

    else:  # input is PNG
        wui_type = "png"
        file_content = await file.read()
        # Reset the stream position of the in-memory file
        image_stream = BytesIO(file_content)
        image_stream.seek(0)
        pil_image = Image.open(image_stream).convert("RGB")
        image_url = db_client.upload_file(file=image_stream, file_extension=".png")
        # upload file metadata to PostGreSQL DB
        data = db_client.insert_file_metadata(
            wui_name=file.filename,
            screenshot_url=image_url,
            html_url=None,
            metrics_to_evaluate=metrics_data.metrics
        )

        metrics = await get_metrics()

        metricsEvaluatorHandler = MetricsDependencyManager(
            wui_id=data['id'],
            pil_image=pil_image.convert("RGB"),
            png_image=image_stream,
            metrics_to_evaluate=metrics_data.metrics,
            url=None,
            html_content=None,
            available_metrics=metrics
        )

        # Add a background task (evaluating the metrics) to run after the response is sent
        background_tasks.add_task(
            metricsEvaluatorHandler.identify_preprocessing_load_metrics_and_evaluate_metrics
        )

    # return the input name as well as result_id which will be used to construct the unique URL for the result page
    return {
        "wui_name": data['wui_name'],
        "result_id": str(data['id']),
        "wui_type": wui_type
    }


class WuiDataType(BaseModel):
    id: str
    created_at: str
    wui_name: str
    screenshot_url: Optional[str] = None
    metrics_to_evaluate: List[str]
    html_url: Optional[str] = None


@app.get('/api/data/{wui_id}', summary="Get metadata of a WUI", description="Get metadata of a WUI based on its ID")
async def get_wui_data_by_wui_id(wui_id: str) -> WuiDataType:
    data = db_client.get_wui_data_by_wui_id(wui_id)
    return data


class ResultType(BaseModel):
    metric_id: str
    results: List[str]


@app.get('/api/result/{wui_id}', summary="Get evaluation results of a WUI", description="Get evaluation results for a specific WUI")
async def get_result_by_wui_id(wui_id: str) -> List[ResultType]:
    data = db_client.get_evaluation_results_by_wui_id(wui_id)
    return data


class MetricExtensionRequestMetadata(BaseModel):
    download_links: List[str]
    email_address: str


@app.post(
    'api/extension',
    summary="Upload files and metadata of the metric requested for extension",
    description="Upload files and metadata of the metric requested for extension"
)
async def insert_new_metric_data(
        background_tasks: BackgroundTasks,
        files: List[UploadFile] = File(...),
        metadata: str = Form(...)
):
    metadata = json.loads(metadata)
    metric_extension_request_metadata: MetricExtensionRequestMetadata = metadata['metricExtensionRequestMetadata']
    download_links = metric_extension_request_metadata.get('download_links')
    email_address = metric_extension_request_metadata.get('email_address')

    requirements_file_url = metric_config_file_url = metric_implementation_file_url = None

    for file in files:
        root, ext = os.path.splitext(file.filename)
        # Do something with each file

        if file.filename == 'requirements.txt':
            requirements_file_url = db_client.upload_file(
                file=file.file,
                file_extension=ext,
                bucket_path='metric_extension',
                content_type=file.content_type
            )
        elif file.filename == 'metric.json':
            metric_config_file_url = db_client.upload_file(
                file=file.file,
                file_extension=ext,
                bucket_path='metric_extension',
                content_type=file.content_type
            )
        else:
            metric_implementation_file_url = db_client.upload_file(
                file=file.file,
                file_extension=ext,
                bucket_path='metric_extension',
                content_type=file.content_type
            )

    if requirements_file_url is None or metric_config_file_url is None or metric_implementation_file_url is None:
        raise HTTPException(status_code=500, detail="Failed to upload file(s)!")

    # upload metric extension metadata to PostGreSQL DB
    data = db_client.insert_metric_extension_request_metadata(
        metric_implementation_file_url=metric_implementation_file_url,
        metric_config_file_url=metric_config_file_url,
        requirements_file_url=requirements_file_url,
        metric_required_models_download_links=download_links,
        metric_requester_email_address=email_address
    )

    # Prepare email notification to be sent to the admin
    subject = "New Metric Extension Request"

    content = create_email_content(
        metric_implementation_file_url,
        requirements_file_url,
        metric_config_file_url,
        email_address,
        download_links
    )

    background_tasks.add_task(send_email, subject, content)

    return data
