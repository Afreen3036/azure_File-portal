import os
from flask import Flask, render_template, request, redirect, url_for
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
from azure.identity import DefaultAzureCredential

app = Flask(__name__)

# This will pull your storage name from Azure settings later
ACCOUNT_NAME = os.getenv('STORAGE_ACCOUNT_NAME')
ACCOUNT_URL = f"https://{ACCOUNT_NAME}.blob.core.windows.net"
CONTAINER_NAME = "uploads"

# Security: Managed Identity (No keys in code!)
credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(ACCOUNT_URL, credential=credential)

@app.route('/')
def index():
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    # List all files in storage
    blobs = container_client.list_blobs()
    return render_template('index.html', blobs=blobs)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=file.filename)
        blob_client.upload_blob(file.read(), overwrite=True)
    return redirect('/')

@app.route('/download/<blob_name>')
def download_file(blob_name):
    # 1. Define the timeframe for the delegation key (Required for Managed Identity)
    start_time = datetime.utcnow()
    expiry_time = start_time + timedelta(hours=1)
    
    # 2. Get the delegation key correctly
    user_delegation_key = blob_service_client.get_user_delegation_key(
        key_start_time=start_time,
        key_expiry_time=expiry_time
    )

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # 3. Generate the SAS using the delegation key
    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_name,
        user_delegation_key=user_delegation_key, # Use the key we just generated
        permission=BlobSasPermissions(read=True),
        expiry=expiry_time
    )

    download_url = f"{blob_client.url}?{sas_token}"
    return redirect(download_url)

if __name__ == '__main__':
    app.run()

    
