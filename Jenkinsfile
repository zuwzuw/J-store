pipeline {
    agent any

    environment {
        REPO_URL = 'https://github.com/zuwzuw/J-store.git' // URL репозитория
        
    }

    stages {
        stage('Clone') {
            steps {
                echo 'Cloning repository...'
                git branch: 'main', url: "${REPO_URL}"
                echo 'Repository cloned successfully!'
            }
        }

        stage('Build') {
            steps {
                echo 'Building Docker containers...'
                sh 'docker-compose build'
                echo 'Build completed successfully!'
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
                sh 'pytest tests/' // Обновите путь, если ваши тесты находятся в другом месте
                echo 'Tests executed successfully!'
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                sh 'docker-compose up -d'
                echo 'Application deployed successfully!'
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution finished!'
        }
        failure {
            echo 'Pipeline failed! Please check the logs.'
        }
    }
}
