pipeline {
  agent any

  environment {
    DOCKER_CREDS   = credentials('dockerhub-credentials')
    K3S_FILE       = credentials('k3s-kubeconfig')   // Secret file
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
        sh """#!/bin/bash
          echo "Logging in to Docker Hub..."
          echo "$DOCKER_CREDS_PSW" | docker login -u "$DOCKER_CREDS_USR" --password-stdin

          docker buildx create --use || true

          echo "Building and pushing image..."
          docker buildx build \
            --platform linux/amd64 \
            -t "$REPO_URI:$GIT_COMMIT" \
            -t "$REPO_URI:latest" \
            --push .
        """
      }
    }

    stage('Deploy to k3s') {
      steps {
        withCredentials([file(credentialsId: 'k3s-kubeconfig', variable: 'KCFG')]) {
          sh """#!/bin/bash
            echo "Using kubeconfig from Jenkins credentials..."
            export KUBECONFIG="$KCFG"

            echo "Testing KUBECONFIG..."
            kubectl config get-contexts || exit 1

            echo "Applying manifests..."
            kubectl apply -f k8s/

            echo "Updating deployment image..."
            kubectl set image deployment/flask-api \
              flask-api="$REPO_URI:$GIT_COMMIT" \
              -n "$K8S_NAMESPACE"
          """
        }
      }
    }
  }
}
