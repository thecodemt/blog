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
                    image 'python:3.9'  // 使用 Python 3.8 的 Docker 镜像
                    args '-u root'  // 以 root 身份运行容器
                }
            }
            steps {
                // 安装依赖
                sh 'pip install --upgrade pip'
                sh 'pip install -r requirements.txt'
                
                // 运行测试
                sh 'pytest tests/'
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