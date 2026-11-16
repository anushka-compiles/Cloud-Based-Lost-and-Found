# Cloud-Based Lost and Found Management System

A cloud-based web application designed to help college students and staff report, search, and recover lost and found items efficiently.

## Project Overview

The **Cloud-Based Lost and Found Management System** provides a centralized platform where users can report lost or found belongings, browse available listings, submit claims, and track recovery requests.

The application uses Python and Flask for backend development and AWS cloud services for data storage and deployment.

## Objectives

- Provide a centralized platform for lost and found items.
- Allow users to report lost and found belongings.
- Enable users to search and filter item listings.
- Support image uploads for item identification.
- Allow users to submit claims for lost belongings.
- Provide administrators with claim management capabilities.
- Demonstrate the practical use of cloud computing services.

## Technologies Used

| Category | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | Flask |
| Frontend | HTML, CSS, JavaScript |
| Database | Amazon DynamoDB |
| Image Storage | Amazon S3 |
| Cloud Deployment | AWS Elastic Beanstalk |
| Access Management | AWS IAM |
| Application Server | Gunicorn |

## Key Features

1. **User Authentication** – User registration and login.
2. **Lost Item Reporting** – Submit details of lost belongings.
3. **Found Item Reporting** – Upload details of found belongings.
4. **Image Upload** – Attach item photographs using Amazon S3.
5. **Search and Filter** – Browse listings to identify matching items.
6. **Possible Item Matching** – Rule-based matching of lost and found reports.
7. **Claim Management** – Submit claims for items.
8. **Admin Management** – Review and approve or reject claims.

## Cloud Architecture

The application follows a cloud-based architecture:

1. Users access the application through a web browser.
2. The Flask application processes user requests.
3. Amazon DynamoDB stores user, item, and claim information.
4. Amazon S3 stores uploaded item photographs.
5. AWS Elastic Beanstalk hosts the web application.
6. AWS IAM manages permissions for cloud resource access.

## Database Tables

The project uses the following DynamoDB tables:

- `lostfound-users`
- `lostfound-items`
- `lostfound-claims`

## Project Structure

```text
Cloud-Based-Lost-and-Found/
│
├── application.py
├── claims.py
├── matching.py
├── s3_service.py
├── requirements.txt
├── Procfile
├── .gitignore
│
├── static/
│   └── style.css
│
└── templates/
    ├── admin.html
    ├── base.html
    ├── claim.html
    ├── index.html
    ├── item_detail.html
    ├── login.html
    ├── register.html
    ├── report.html
    └── search.html
```

## Local Installation and Execution

### 1. Clone the repository

```bash
git clone https://github.com/anushka-compiles/Cloud-Based-Lost-and-Found.git
```

### 2. Navigate to the project directory

```bash
cd Cloud-Based-Lost-and-Found
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment (Windows)

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure AWS

Configure AWS credentials securely and ensure the application has the required permissions to access DynamoDB and S3.

Set the required application configuration and secret key through environment variables where applicable. Do not commit AWS credentials or secret keys to GitHub.

### 7. Run the application

```bash
python application.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

## Live Application

**Deployed using:** AWS Elastic Beanstalk

[Open the Live Application](http://cloud-lost-found-env.eba-qbimec97.ap-southeast-2.elasticbeanstalk.com)

## Future Enhancements

- Email notifications for claim updates.
- Advanced image-based item recognition.
- Improved matching using machine learning.
- Mobile-friendly application interface.
- Analytics dashboard for administrators.

## Academic Project

**Project Title:** Cloud-Based Lost and Found Management System Using Python and Cloud Storage

**Developed By:** Anushka G G

**Department:** Electronics and Communication Engineering

**Course:** Introduction to Cloud Computing and Edge Computing

**Project Type:** Individual Academic Mini-Project

---

Individually designed and developed to demonstrate the practical application of cloud computing technologies in solving real-world problems.
