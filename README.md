
First registered user will be ADMIN
or defaul credentials
admin@example.com
admin

This guide will help you set up and run the Flask application in a Dockerized environment.

    Prerequisites

    Make sure you have the following tools installed on your system:

    Docker (latest version)

    Docker Compose (latest version)

    Project Structure

    The project contains the following key files:

    Dockerfile: Used to containerize the Flask application.

    docker-compose.yml: Defines and configures the services required for the application.

    Flask application source code.

    Steps to Set Up and Run the Flask Application

    Clone the Repository:

    git clone https://github.com/zuwzuw/J-store.git
    cd J-store

    Build and Start the Services:
    Navigate to the project directory and use Docker Compose to build and start the application:

    docker-compose up --build

    This command will:

    Build the Docker image for the Flask application as defined in the Dockerfile.

    Start the Flask application on port 5000.

    Access the Application:
    Open your web browser and navigate to:

    http://localhost:5000

    The Flask application should now be running.

    Managing the Application

    Stop the Services:
    To stop the running services, press Ctrl+C in the terminal where the docker-compose command was run, or execute:

    docker-compose down

    Rebuild Services:
    If you make changes to the application code or configuration, rebuild the services using:

    docker-compose up --build

    Notes

    Make sure port 5000 is not already in use by another application.

    The application is set to run in production mode by default. Adjust the FLASK_ENV variable in the docker-compose.yml file if needed.

    For further information or troubleshooting, refer to the Docker and Flask documentation