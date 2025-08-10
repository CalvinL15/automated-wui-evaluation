from io import BytesIO
from typing import List

from dotenv import load_dotenv
import os
from supabase import create_client, Client
import uuid

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def upload_file(
        file: BytesIO,
        file_extension: str,
        bucket_id: str = 'wui-auto-evaluation',
        content_type: str = "image/png",
        bucket_path: str = 'input_files'
):
    """
    Uploads an in-memory file (WUI input or WUI evaluation result) to a specified Supabase storage bucket.

    :param content_type: The file content type
    :param file_extension: The file extension
    :param bucket_id: The ID of the bucket where the file will be stored
    :param bucket_path: The name of the folder within the bucket where the file will be stored
    :param file: The file to be uploaded
    """

    file.seek(0)

    # upload file to supabase storage
    file_content = file.read()
    if not file_content:
        raise ValueError("File content is empty!")

    full_path = bucket_path + '/' + str(uuid.uuid4()) + file_extension

    response = supabase.storage.from_(bucket_id).upload(
        path=full_path, file=file_content, file_options={"content-type": content_type}
    )

    if response.status_code in [200, 201]:
        # After successful upload, get the public URL
        public_url = supabase.storage.from_(bucket_id).get_public_url(full_path)
        if public_url:
            return public_url
        else:
            raise ValueError(f"Failed to retrieve file URL!")
    else:
        raise ValueError(f"Failed to upload file: {response.error_message}")


def insert_file_metadata(wui_name: str, screenshot_url: str, html_url: str, metrics_to_evaluate: List[str]):
    """
    Insert the metadata of the WUI input to a Supabase postgreSQL DB.
    """
    try:
        response = supabase.table('wui_input').insert(
            {
                "wui_name": wui_name,
                "screenshot_url": screenshot_url,
                "html_url": html_url,
                "metrics_to_evaluate": metrics_to_evaluate
            }
        ).execute()
        return response.data[0]
    except Exception as e:
        print(f"An exception occurred: {e}")
        return None


def insert_metric_result_metadata(wui_id: str, metric_id: str, results: List[str]):
    """
    Insert the metric evaluation result of a WUI to a Supabase postgreSQL DB.
    """
    response = supabase.table('result').insert(
        {
            "wui_id": wui_id,
            "metric_id": metric_id,
            "results": results
        }
    ).execute()
    return response.data[0]


def get_evaluation_results_by_wui_id(wui_id: str):
    """
    Retrieve evaluation results of a WUI by its ID.
    """
    response = supabase.table('result').select('metric_id', 'results').eq('wui_id', uuid.UUID(wui_id)).execute()
    return response.data


def get_wui_data_by_wui_id(wui_id: str):
    """
    Retrieve metadata of a WUI by its ID.
    """
    response = supabase.table('wui_input').select('*').eq('id', uuid.UUID(wui_id)).execute()
    return response.data[0]


def insert_metric_extension_request_metadata(
        metric_implementation_file_url: str,
        requirements_file_url: str,
        metric_config_file_url: str,
        metric_requester_email_address: str = '',
        metric_required_models_download_links: List[str] = []
):
    """
    Insert the metadata of the request for a new metric to a Supabase postgreSQL DB.
    """
    response = supabase.table('metric_extension').insert(
        {
            "metric_implementation_file_url": metric_implementation_file_url,
            "requirements_file_url": requirements_file_url,
            "metric_config_file_url": metric_config_file_url,
            "metric_requester_email_address": metric_requester_email_address,
            "metric_required_models_download_links": metric_required_models_download_links
        }
    ).execute()

    return response.data[0]


def get_approved_metrics():
    """
    Retrieve list of metrics approved for extension
    """

    response = supabase.table("metric_extension").select(
        'id',
        'metric_implementation_file_url',
        'requirements_file_url',
        'metric_config_file_url',
        'metric_required_models_download_links',
        'is_processed'
    ).eq('is_approved', True).execute()

    return response.data


def mark_metric_as_processed(metric_uid):
    """
    Mark a metric extension request as processed
    """
    supabase.table("metric_extension").update({'is_processed': True}).eq('id', metric_uid).execute()

