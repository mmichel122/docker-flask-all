pipeline {
  agent any

  environment {
    AWS_REGION = "us-east-1"
    IMAGE_NAME = "flask-api-demo"
    REPO_URI   = "637423311003.dkr.ecr.us-east-1.amazonaws.com/mlops/demo"
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
          echo "🔨 Building Docker image..."

          # Build once using commit SHA
          docker build -t ${IMAGE_NAME}:${GIT_COMMIT} .
        """
      }
    }

    stage('Tag Images') {
      steps {
        sh """
          echo "🏷️ Tagging images..."

          # Tag immutable version
          docker tag ${IMAGE_NAME}:${GIT_COMMIT} ${REPO_URI}:${GIT_COMMIT}

          # Tag mutable latest
          docker tag ${IMAGE_NAME}:${GIT_COMMIT} ${REPO_URI}:latest
        """
      }
    }

    stage('Push to ECR') {
      steps {
        withAWS(credentials: 'aws-creds', region: "${AWS_REGION}") {
          sh """
            echo "💾 Logging into ECR..."
            aws ecr get-login-password --region ${AWS_REGION} \
              | docker login --username AWS --password-stdin ${REPO_URI}

            echo "📤 Pushing images to ECR..."

            # Push both tags
            docker push ${REPO_URI}:${GIT_COMMIT}
            docker push ${REPO_URI}:latest
          """
        }
      }
    }

    // --- Optional: Auto Deploy to EKS ---
    // stage('Deploy to EKS') {
    //   steps {
    //     withAWS(credentials: 'aws-creds', region: "${AWS_REGION}") {
    //       sh """
    //         aws eks update-kubeconfig --region ${AWS_REGION} --name mlops-demo
    //         kubectl set image deployment/flask-api \
    //             flask-api=${REPO_URI}:${GIT_COMMIT} -n default
    //       """
    //     }
    //   }
    // }

  }
}

