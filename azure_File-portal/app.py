import os
from io import BytesIO

from flask import Flask, abort, redirect, render_template, request, send_file, url_for
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

app = Flask(__name__)

CONTAINER_NAME = os.getenv("STORAGE_CONTAINER_NAME", "uploads")


def _create_blob_service_client():
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if connection_string:
        return BlobServiceClient.from_connection_string(connection_string)

    account_name = os.getenv("STORAGE_ACCOUNT_NAME")
    if not account_name:
        raise RuntimeError(
            "Set AZURE_STORAGE_CONNECTION_STRING or STORAGE_ACCOUNT_NAME."
        )
    account_url = f"https://{account_name}.blob.core.windows.net"
    return BlobServiceClient(account_url, credential=DefaultAzureCredential())


blob_service_client = _create_blob_service_client()

@app.route('/')
def index():
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    # List all files in storage
    blobs = container_client.list_blobs()
    return render_template('index.html', blobs=blobs)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get("file")
    if file and file.filename:
        blob_client = blob_service_client.get_blob_client(
            container=CONTAINER_NAME, blob=file.filename
        )
        blob_client.upload_blob(file.read(), overwrite=True)
    return redirect('/')

@app.route("/download/<path:blob_name>")
def download_file(blob_name):
    blob_client = blob_service_client.get_blob_client(
        container=CONTAINER_NAME, blob=blob_name
    )

    try:
        blob_stream = blob_client.download_blob()
        data = blob_stream.readall()
        properties = blob_client.get_blob_properties()
    except ResourceNotFoundError:
        abort(404, description="File not found.")
    except HttpResponseError:
        abort(500, description="Unable to download file.")

    content_type = "application/octet-stream"
    if properties.content_settings and properties.content_settings.content_type:
        content_type = properties.content_settings.content_type

    return send_file(
        BytesIO(data),
        mimetype=content_type,
        as_attachment=True,
        download_name=os.path.basename(blob_name) or blob_name,
    )

@app.route("/delete/<path:blob_name>")
def delete_file(blob_name):
    blob_client = blob_service_client.get_blob_client(
        container=CONTAINER_NAME, blob=blob_name
    )

    try:
        blob_client.delete_blob()
    except ResourceNotFoundError:
        pass
    except HttpResponseError:
        abort(500, description="Unable to delete file.")

    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run()

    
