pipeline {
  agent any

  environment {
    AWS_REGION    = "us-east-1"
    IMAGE_NAME    = "flask-api-demo"
    REPO_URI      = "637423311003.dkr.ecr.us-east-1.amazonaws.com/mlops/demo"
    K8S_NAMESPACE = "demo"
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build & Push (AMD64)') {
      steps {
        withAWS(credentials: 'aws-creds', region: "${AWS_REGION}") {
          sh """
            echo "Logging in to ECR..."
            aws ecr get-login-password --region ${AWS_REGION} \
              | docker login --username AWS --password-stdin ${REPO_URI}

            echo "Setting up Docker Buildx..."
            docker buildx create --use || true

            echo "Building and pushing AMD64 image..."
            docker buildx build \
              --platform linux/amd64 \
              -t ${REPO_URI}:${GIT_COMMIT} \
              -t ${REPO_URI}:latest \
              --push .
          """
        }
      }
    }

    stage('Deploy to EKS') {
      steps {
        withAWS(credentials: 'aws-creds', region: "${AWS_REGION}") {
          sh """
            echo "Updating kubeconfig..."
            aws eks update-kubeconfig --region ${AWS_REGION} --name mlops-demo

            echo "Applying Kubernetes manifests..."
            kubectl apply -f k8s/namespace.yaml
            kubectl apply -f k8s/deployment.yaml
            kubectl apply -f k8s/service.yaml

            echo "Updating deployment image to new commit..."
            kubectl set image deployment/flask-api \
              flask-api=${REPO_URI}:${GIT_COMMIT} \
              -n ${K8S_NAMESPACE}

            echo "Deployment updated."
          """
        }
      }
    }
  }
}

