pipeline {
    agent any
    
    environment {
        DOCKER_USERNAME = credentials('docker-hub-username')
        DOCKER_PASSWORD = credentials('docker-hub-password')
        IMAGE_NAME = 'blog'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Test') {
            agent {
                docker {
                    image 'python:3.9'
                    args '-v $WORKSPACE:/app'
                }
            }
            steps {
                sh '''
                    cd /app
                    pip install -r requirements.txt
                    python -m pytest tests/ --junitxml=test-results/junit.xml
                '''
            }
            post {
                always {
                    junit 'test-results/junit.xml'
                }
            }
        }
        
        
        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t ${DOCKER_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG} .
                    docker build -t ${DOCKER_USERNAME}/${IMAGE_NAME}:latest .
                '''
            }
        }
        
        stage('Push Docker Image') {
            steps {
                sh '''
                    echo ${DOCKER_PASSWORD} | docker login -u ${DOCKER_USERNAME} --password-stdin
                    docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}
                    docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:latest
                '''
            }
        }
        
        stage('Deploy') {
            steps {
                sh '''
                    # 创建 .env 文件
                    echo "DOCKER_USERNAME=${DOCKER_USERNAME}" > .env
                    echo "IMAGE_TAG=${IMAGE_TAG}" >> .env
                    
                    # 部署应用
                    docker-compose down
                    docker-compose pull
                    docker-compose up -d
                '''
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}