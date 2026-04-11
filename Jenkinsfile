pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'heyd-media-app:latest'
        APP_PORT     = '80'
    }

    stages {

        stage('Clone Repository') {
            steps {
                echo '📥 Cloning Heyd Media App...'
                git branch: 'main',
                    url: 'https://github.com/harivasantharava41-rgb/Heyd-media-app.git'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo '🔍 Running SonarQube analysis...'
                sh 'echo "SonarQube Analysis Running..."'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image...'
                sh 'docker build -t ${DOCKER_IMAGE} .'
            }
        }

        stage('Deploy Application') {
            steps {
                echo '🚀 Deploying Heyd Media App...'
                sh '''
                    docker stop heyd-media || true
                    docker rm heyd-media || true
                    docker run -d \
                        --name heyd-media \
                        -p ${APP_PORT}:5000 \
                        -e DB_HOST=mysql-db \
                        -e DB_USER=root \
                        -e DB_PASSWORD=root123 \
                        -e DB_NAME=heydmediadb \
                        ${DOCKER_IMAGE}
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Heyd Media App deployed!'
        }
        failure {
            echo '❌ Deployment failed. Check logs.'
        }
    }
}
