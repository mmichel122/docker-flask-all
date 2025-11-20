pipeline {
  agent any

  environment {
    DOCKER_CREDS = credentials('dockerhub-credentials')

    DEV_REPO     = "mmocker06/fastapi-app-dev"
    RELEASE_REPO = "mmocker06/fastapi-app"

    GITOPS_REPO  = "/tmp/gitops"
    GITOPS_URL   = "https://github.com/mmichel122/argocd-k8s-automation.git"

    IMAGE_NAME   = "fastapi-app"
  }

  stages {

    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Unit Tests') {
      steps {
        sh "pytest -q || true"
      }
    }

    stage('Build & Push Docker Image') {
      steps {
        script {

          sh """
            echo "${DOCKER_CREDS_PSW}" | docker login -u "${DOCKER_CREDS_USR}" --password-stdin
            docker buildx create --use || true
          """

          // PRs → DEV
          if (env.BRANCH_NAME ==~ /PR-.*/) {

            sh """
              docker buildx build \
                --platform linux/amd64 \
                -t ${DEV_REPO}:latest \
                --push \
                .
            """
          }

          // main/master → RELEASE stable + latest
          else if (env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'master') {

            sh """
              docker buildx build \
                --platform linux/amd64 \
                -t ${RELEASE_REPO}:stable \
                -t ${RELEASE_REPO}:latest \
                --push \
                .
            """
          }
        }
      }
    }


    stage('Update GitOps Repo') {
      when { branch 'main' }
      steps {
        sh """
          echo "Updating GitOps Repo…"

          rm -rf ${GITOPS_REPO}
          git clone ${GITOPS_URL} ${GITOPS_REPO}

          sed -i 's/tag: .*/tag: "stable"/' \
            ${GITOPS_REPO}/charts/fastapi-app/values.yaml

          cd ${GITOPS_REPO}
          git config user.email "modusmitch@gmail.com"
          git config user.name "mmichel122"
          git add .
          git commit -m "Pipeline: update stable image tag"
          git push origin main
        """
      }
    }

  }
}
