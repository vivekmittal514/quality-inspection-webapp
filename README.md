# Image Quality Analysis System

## Overview
This system allows users to upload images and automatically analyze their quality using AWS services. It determines if an image is "good" or "defective" using Amazon SageMaker for inference.

## Architecture
- Amazon S3: Image storage
- Amazon CloudFront: Content delivery
- AWS Lambda: Serverless computing
- Amazon API Gateway: REST API endpoints
- Amazon DynamoDB: Storing analysis results
- Amazon SageMaker: Image quality analysis

## Features
- Single-page web application for image uploads
- Real-time image quality analysis
- Historical view of uploaded images and their analysis results
- Serverless backend architecture
- Secure file uploads using pre-signed URLs
- Content delivery through CloudFront

## Prerequisites
- AWS Account
- AWS SAM CLI
- Node.js 16.x or later
- Python 3.9 or later
- A trained SageMaker model endpoint

## Setup and Deployment
1. Clone the repository:
```bash
git clone https://github.com/vivekmittal514/quality-inspection-webapp.git
cd quality-inspection-webapp
```
2. Build and deploy using sam template:
```bash
sam build
sam deploy --guided
```
During the guided deployment, you'll need to provide:
* Stack name
* AWS Region
* Bucket name for uploads
* Domain name for CloudFront
* SageMaker endpoint name

## Project Structure
.
├── README.md
├── template.yaml             # SAM template
├── frontend/
│   └── index.html           # Web interface
├── lambda/
│   ├── analyze-image/       # Image analysis Lambda function
│   │   └── app.py
│   ├── get-history/         # History retrieval Lambda function
│   │   └── app.py
│   └── getSignedURL/        # S3 upload URL Lambda function
│       └── app.js

# API Endpoints
GET /uploads - Get pre-signed URL for S3 upload
POST /analyze-image - Trigger image analysis
GET /get-history - Retrieve upload history
# Usage
Open the web interface through the CloudFront URL
Select a JPEG image to upload
The system will automatically:
Upload the image to S3
Analyze the image quality
Display the analysis results
Store the results in history
View previous uploads and their analysis results in the history section
# Contributing
Fork the repository
Create your feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request

# License
This project is licensed under the MIT License - see the [LICENSE](https://console.harmony.a2z.com/LICENSE) file for details

# Acknowledgments
AWS SAM documentation
Vue.js framework
AWS Lambda documentation
Amazon SageMaker documentation

# Security
This application implements several security best practices:

S3 bucket with blocked public access
CloudFront Origin Access Control
Pre-signed URLs for uploads
API Gateway authorization
VPC configuration for Lambda functions

# Support
For support, please open an issue in the GitHub repository or contact the maintainers.


