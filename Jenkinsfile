pipeline {
  agent any

  environment {
    DOCKER_CREDS = credentials('dockerhub-credentials')

    DEV_REPO     = "mmdocker06/fastapi-app-dev"
    RELEASE_REPO = "mmdocker06/fastapi-app"

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

          //
          // PR builds → fastapi-app-dev:pr-##
          //
          if (env.BRANCH_NAME ==~ /PR-.*/) {

            def DEV_TAG = "pr-${CHANGE_ID}"

            sh """
              docker buildx build \
                --platform linux/amd64 \
                -t ${DEV_REPO}:${DEV_TAG} \
                -t ${DEV_REPO}:latest \
                --push \
                app
            """

          } 
          //
          // MAIN RELEASE BUILDS → fastapi-app:<BUILD_NUMBER> + latest
          //
          else if (env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'master') {

            def VERSION_TAG = "${BUILD_NUMBER}"
            env.RELEASE_TAG = VERSION_TAG

            sh """
              docker buildx build \
                --platform linux/amd64 \
                -t ${RELEASE_REPO}:${VERSION_TAG} \
                -t ${RELEASE_REPO}:latest \
                --push \
                app
            """
          }
        }
      }
    }

    stage('Update GitOps Repo') {
      when {
        anyOf {
          branch 'main'
          branch 'master'
        }
      }

      steps {
          withCredentials([usernamePassword(
              credentialsId: 'github-creds',
              usernameVariable: 'GIT_USER',
              passwordVariable: 'GIT_PAT'
          )]) {

              script {
                  sh """
                    echo "Updating GitOps Repo with tag ${RELEASE_TAG}"

                    rm -rf ${GITOPS_REPO}
                    git clone https://${GIT_USER}:${GIT_PAT}@github.com/mmichel122/argocd-k8s-automation.git ${GITOPS_REPO}

                    sed -i 's/tag: .*/tag: "${RELEASE_TAG}"/' \
                      ${GITOPS_REPO}/charts/fastapi-app/values.yaml

                    cd ${GITOPS_REPO}
                    git config user.email "modusmitch@gmail.com"
                    git config user.name "mmichel122"
                    git add .
                    git commit -m "Pipeline: update release image tag to ${RELEASE_TAG}"
                    git push https://${GIT_USER}:${GIT_PAT}@github.com/mmichel122/argocd-k8s-automation.git main
                  """
              }
          }
      }
    }
  }
}
