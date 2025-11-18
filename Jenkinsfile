pipeline {
  agent any

  environment {
    AWS_REGION   = "us-east-1"
    IMAGE_NAME   = "flask-api-demo"
    REPO_URI     = "637423311003.dkr.ecr.us-east-1.amazonaws.com/mlops/demo"
    K8S_NAMESPACE = "demo"
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build Docker Image') {
      steps {
        sh """
          docker build -t ${IMAGE_NAME}:${GIT_COMMIT} .
          docker tag ${IMAGE_NAME}:${GIT_COMMIT} ${IMAGE_NAME}:latest
        """
      }
    }

    stage('Push to ECR') {
      steps {
        withAWS(credentials: 'aws-creds', region: "${AWS_REGION}") {
          sh """
            aws ecr get-login-password --region ${AWS_REGION} \
              | docker login --username AWS --password-stdin ${REPO_URI}

            docker tag ${IMAGE_NAME}:${GIT_COMMIT} ${REPO_URI}:${GIT_COMMIT}
            docker tag ${IMAGE_NAME}:${GIT_COMMIT} ${REPO_URI}:latest

            docker push ${REPO_URI}:${GIT_COMMIT}
            docker push ${REPO_URI}:latest
          """
        }
      }
    }

    stage('Deploy to EKS') {
      steps {
        withAWS(credentials: 'aws-creds', region: "${AWS_REGION}") {
          sh """
            aws eks update-kubeconfig --region ${AWS_REGION} --name mlops-demo

            kubectl apply -f k8s/namespace.yaml
            kubectl apply -f k8s/deployment.yaml
            kubectl apply -f k8s/service.yaml

            kubectl set image deployment/flask-api \
              flask-api=${REPO_URI}:${GIT_COMMIT} \
              -n ${K8S_NAMESPACE}
          """
        }
      }
    }
  }
}

