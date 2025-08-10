import os
from typing import List, Union

import aiosmtplib
from email.message import EmailMessage

SMTP_HOST = "smtp.gmail.com"
SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')

SMTP_PORT = 587
ADMIN_EMAIL = "wui.eval@gmail.com"


# helper function
def validate_download_links(links: Union[str, List[str]]) -> str:
    if isinstance(links, list):
        # Check if the list is empty or contains only empty strings
        if not links or all(not link.strip() for link in links):
            return "not provided"
    elif isinstance(links, str):
        # Check if the string is empty or contains only whitespace
        if not links.strip():
            return "not provided"
    return links


def create_email_content(
    metric_implementation_file_url: str,
    requirements_file_url: str,
    metric_config_file_url: str,
    email_address: str,
    download_links: Union[str, List[str]]
):
    return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                }}
                .container {{
                    margin: 10px;
                }}
                .header {{
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .section {{
                    margin-bottom: 10px;
                }}
                .section a {{
                    color: #1a73e8;
                    text-decoration: none;
                }}
                .section a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">A new metric extension request has been submitted. Please take a look as soon as possible!</div>
                <div class="section">
                    <strong>Metric Implementation file URL:</strong> 
                    <br/>
                    <a href="{metric_implementation_file_url}">{metric_implementation_file_url}</a>
                </div>
                <div class="section">
                    <strong>Metric dependency requirements file URL:</strong> 
                    <br/>
                    <a href="{requirements_file_url}">{requirements_file_url}</a>
                </div>
                <div class="section">
                    <strong>Metric config file URL:</strong> 
                    <br/>
                    <a href="{metric_config_file_url}">{metric_config_file_url}</a>
                </div>
                <div class="section">
                    <strong>Requester Email:</strong> 
                    <p>{email_address}</p>
                </div>
                <div class="section">
                    <strong>Model Download Links:</strong> 
                    <p>{validate_download_links(download_links)}</p>
                </div>
            </div>
            <br/>
            <br/>
            <br/>
            <div class="section">
                The metric extension can be approved manually by configuring the <b>is_approved</b> boolean value of the database table "metric_extension" in Supabase.
            </div>
        </body>
        </html>
    """


async def send_email(subject: str, content: str):
    message = EmailMessage()
    message["From"] = SMTP_USER
    message["To"] = ADMIN_EMAIL
    message["Subject"] = subject
    message.set_content(content)
    message.add_alternative(content, subtype='html')

    await aiosmtplib.send(
        message,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USER,
        password=SMTP_PASSWORD,
        start_tls=True
    )