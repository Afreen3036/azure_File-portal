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
    # Generates a secure temporary link valid for 1 hour
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    
    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=None, 
        user_delegation_key=blob_service_client.get_user_delegation_key(datetime.utcnow(), datetime.utcnow() + timedelta(hours=1)),
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)
    )
    
    download_url = f"{blob_client.url}?{sas_token}"
    return redirect(download_url)

@app.route('/delete/<blob_name>')
def delete_file(blob_name):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_client.delete_blob()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()

    
