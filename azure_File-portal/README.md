# azure_File-portal

A secure and cost-efficient web application built to manage file uploads and downloads using Microsoft Azure services. This project demonstrates the integration of Python Flask with Azure's managed services.

## Architecture & Services
This project utilizes the following Azure components:
* **Azure App Service (Linux):** Hosts the Python Flask web application.
* **Azure Blob Storage:** Used as the backend storage for all uploaded documents.
* **Application Insights:** Integrated for real-time monitoring, telemetry, and logging.
* **GitHub Actions:** Provides a CI/CD pipeline for automated deployment.

## Security Features
* **Managed Identity:** The application uses a System-Assigned Managed Identity to authenticate with Azure Storage. No connection strings or passwords are stored in the code.
* **RBAC (Role-Based Access Control):** The Web App is granted the 'Storage Blob Data Contributor' role to ensure the principle of least privilege.
* **HTTPS Enforcement:** The portal is configured to only allow secure encrypted traffic.

## Cost-Aware Design
To ensure the project remains cost-effective:
* **F1 Free Tier:** The App Service runs on the free pricing tier.
* **LRS (Locally Redundant Storage):** Blob storage is configured with LRS to provide the lowest cost while maintaining data durability within a single region.

## Deployment Instructions
1. **Repository Structure:**
   - `app.py`: The main Flask application.
   - `requirements.txt`: Python dependencies (Flask, Gunicorn, Azure SDKs).
   - `templates/`: Folder containing the HTML frontend.
   
2. **Startup Command:**
   The application uses Gunicorn as the production web server:
   `gunicorn --bind=0.0.0.0 --timeout 600 app:app`

3. **Environment Variables:**
   The following configuration must be set in the Azure Web App:
   - `STORAGE_ACCOUNT_NAME`: The name of your Azure Storage account.

## 📈 Monitoring
Monitoring is handled via **Application Insights**, allowing us to track:
- Server response times.
- Failed requests or exceptions.
- Overall application health.
