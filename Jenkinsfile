pipeline {
  agent any

  environment {
    DOCKER_CREDS   = credentials('dockerhub-credentials')
    K3S_CONFIG     = credentials('k3s-kubeconfig')
    IMAGE_NAME     = "flask-api-demo"
    REPO_URI       = "docker.io/${DOCKER_CREDS_USR}/${IMAGE_NAME}"
    K8S_NAMESPACE  = "demo"
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build & Push to Docker Hub') {
      steps {
        sh """
          echo "Logging into Docker Hub..."
          echo "${DOCKER_CREDS_PSW}" | docker login -u "${DOCKER_CREDS_USR}" --password-stdin

          docker buildx create --use || true

          docker buildx build \
            --platform linux/amd64 \
            -t ${REPO_URI}:${GIT_COMMIT} \
            -t ${REPO_URI}:latest \
            --push .
        """
      }
    }

    stage('Deploy to k3s') {
      steps {
        withCredentials([file(credentialsId: 'k3s-kubeconfig', variable: 'KCFG')]) {
          sh '''
            echo "Using kubeconfig from Jenkins credentials..."

            export KUBECONFIG="$KCFG"

            kubectl config get-contexts

            kubectl apply -f k8s/

            kubectl set image deployment/flask-api \
              flask-api=docker.io/${DOCKER_CREDS_USR}/flask-api-demo:${GIT_COMMIT} \
              -n demo
          '''
        }
      }
    }
  }
}
