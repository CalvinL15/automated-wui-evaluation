import subprocess
import json
import os
import aiohttp
from db_client import mark_metric_as_processed


async def process_approved_metric(metric):

    is_processed = metric["is_processed"]

    metric_uid = metric['id']
    config_file_url = metric["metric_config_file_url"]
    # Download the metric config file
    config_file_path = await download_file(config_file_url, f"{metric_uid}_config.json")
    # Load and append the metric config to available metrics
    with open(config_file_path, 'r') as config_file:
        config_data = json.load(config_file)

    metric_id = next(iter(config_data))
    metric_name = config_data[metric_id]["name"]
    implementation_file_path = f"metrics_evaluator/metrics/{metric_id}_{metric_name}.py"

    if not is_processed or not os.path.exists(implementation_file_path):
        implementation_file_url = metric["metric_implementation_file_url"]
        requirements_file_url = metric["requirements_file_url"]
        # Download implementation file
        await download_file(implementation_file_url, implementation_file_path)
        mark_metric_as_processed(metric_uid)

        requirements_file_path = await download_file(requirements_file_url, f"{metric_uid}_requirements.txt")

        # Install dependencies
        install_dependencies(requirements_file_path)

    return config_data


async def download_file(url, filename):
    # already downloaded before, skip
    if os.path.exists(filename):
        return filename

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.read()
            with open(filename, 'wb') as f:
                f.write(content)
    return filename


def install_dependencies(requirements_file_path):
    subprocess.run(["pip", "install", "-r", requirements_file_path], check=True)

