pipeline {
  agent any

  environment {
    DOCKER_CREDS   = credentials('dockerhub-credentials')
    K3S_CONFIG_FILE = 'k3s.yaml'
    IMAGE_NAME     = "flask-api-demo"
    REPO_URI       = "docker.io/${DOCKER_CREDS_USR}/${IMAGE_NAME}"
    K8S_NAMESPACE  = "demo"
  }

  stages {

    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Prepare kubeconfig') {
      steps {
        echo "Loading kubeconfig from Jenkins credentials..."

        // Correct way: use file credential → Jenkins copies actual file
        withCredentials([file(credentialsId: 'k3s-kubeconfig', variable: 'KCFG')]) {
          sh """
            cp "\$KCFG" ${K3S_CONFIG_FILE}
            chmod 600 ${K3S_CONFIG_FILE}
            export KUBECONFIG=${K3S_CONFIG_FILE}

            echo 'Testing kubeconfig...'
            cat ${K3S_CONFIG_FILE}
            kubectl config get-contexts
          """
        }
      }
    }

    stage('Build & Push Docker image') {
      steps {
        sh """
          echo "Logging in to Docker Hub..."
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
          sh """
            cp "\$KCFG" ${K3S_CONFIG_FILE}
            export KUBECONFIG=${K3S_CONFIG_FILE}

            kubectl apply -f k8s/

            kubectl set image deployment/flask-api \
              flask-api=${REPO_URI}:${GIT_COMMIT} \
              -n ${K8S_NAMESPACE}
          """
        }
      }
    }
  }
}
