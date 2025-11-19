pipeline {
  agent any

  environment {
    DOCKER_CREDS = credentials('dockerhub-credentials')
    IMAGE_NAME   = "flask-api-demo"
    REPO_URI     = "docker.io/${DOCKER_CREDS_USR}/${IMAGE_NAME}"
    K8S_NAMESPACE = "demo"
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build & Push to Docker Hub') {
      steps {
        sh '''
          echo "Logging in to Docker Hub..."
          echo "$DOCKER_CREDS_PSW" | docker login -u "$DOCKER_CREDS_USR" --password-stdin

          docker buildx create --use || true

          echo "Building and pushing image..."
          docker buildx build \
            --platform linux/amd64 \
            -t '${REPO_URI}:'"$GIT_COMMIT" \
            -t '${REPO_URI}:latest' \
            --push .
        '''
      }
    }

    stage('Deploy to k3s') {
      steps {
        withCredentials([file(credentialsId: 'k3s-kubeconfig', variable: 'K3S_FILE')]) {
          sh '''
            echo "Using kubeconfig from Jenkins credentials..."

            # No Groovy interpolation → very important
            export KUBECONFIG="$K3S_FILE"

            echo "Verifying Kubernetes context..."
            kubectl config current-context || true

            echo "Applying manifests..."
            kubectl apply -f k8s/

            echo "Updating image..."
            kubectl set image deployment/flask-api \
              flask-api='${REPO_URI}:'"$GIT_COMMIT" \
              -n '${K8S_NAMESPACE}'
          '''
        }
      }
    }
  }
}
