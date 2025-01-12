pipeline {
    agent any

    environment {
        DOCKER_IMAGE_NAME = 'arcteryxxc/jp-store:latest' // Docker image name
    }

    stages {
        stage('Checkout Repository') {
            steps {
                echo "Cloning repository..."
                git url: 'https://github.com/zuwzuw/J-store.git', branch: 'main'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image..."
                sh "docker build -t ${DOCKER_IMAGE_NAME} ."
            }
        }

        stage('Push Docker Image') {
            steps {
                echo "Pushing Docker image to Docker Hub..."
                sh """
                echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
                docker push ${DOCKER_IMAGE_NAME}
                """
            }
        }

        stage('Run Docker Container') {
            steps {
                echo "Running Docker container..."
                sh "docker run -d -p 5000:5000 ${DOCKER_IMAGE_NAME}"
            }
        }
    }

    post {
        always {
            echo "Cleaning up Docker resources..."
            sh "docker system prune -f"
        }
        success {
            echo "Pipeline completed successfully!"
        }
        failure {
            echo "Pipeline failed. Check logs for details."
        }
    }
}
