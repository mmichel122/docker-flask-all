pipeline {
    agent any

    environment {
        DEV_REPO       = "mmocker06/fastapi-app-dev"
        RELEASE_REPO   = "mmocker06/fastapi-app"
        GITOPS_REPO    = "/tmp/gitops"
        GITOPS_URL     = "https://github.com/mmichel122/argocd-k8s-automation.git"
        IMAGE_NAME     = "fastapi-app"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {

                    script {
                        echo "Authenticating Docker Hub for buildx…"

                        // 🔥 Ensure buildx uses correct Docker config (fix for insufficient_scope)
                        sh """
                            mkdir -p ~/.docker
                            echo "{\\"auths\\": {\\"https://index.docker.io/v1/\\": {\\"auth\\": \\"$(echo -n "${DOCKER_USER}:${DOCKER_PASS}" | base64)\\"}}}" > ~/.docker/config.json
                        """

                        // Info only
                        sh """echo "Logged in as: ${DOCKER_USER}" """

                        if (env.BRANCH_NAME ==~ /PR-.*/) {
                            echo "Building DEV image for PR branch..."

                            DEV_TAG="pr-${CHANGE_ID}"

                            sh """
                                docker buildx create --use || true
                                docker buildx build \
                                    --platform linux/amd64 \
                                    -t ${DEV_REPO}:${DEV_TAG} \
                                    --push \
                                    app
                            """

                        } else if (env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'master') {

                            echo "Building RELEASE image for main/master…"

                            RELEASE_TAG="${BUILD_NUMBER}"
                            env.RELEASE_TAG = RELEASE_TAG

                            sh """
                                docker buildx create --use || true
                                docker buildx build \
                                    --platform linux/amd64 \
                                    -t ${RELEASE_REPO}:${RELEASE_TAG} \
                                    -t ${RELEASE_REPO}:latest \
                                    --push \
                                    app
                            """
                        }
                    }
                }
            }
        }

        stage('Update GitOps Repo') {
            when {
                branch 'main'
            }
            steps {
                sh """
                    echo "Updating GitOps Repo with new tag: ${RELEASE_TAG}"

                    rm -rf ${GITOPS_REPO}
                    git clone ${GITOPS_URL} ${GITOPS_REPO}

                    # Update the Helm chart image tag
                    sed -i 's/tag: .*/tag: "${RELEASE_TAG}"/' \
                        ${GITOPS_REPO}/charts/fastapi-app/values.yaml

                    cd ${GITOPS_REPO}
                    git config user.email "modusmitch@gmail.com"
                    git config user.name "mmichel122"

                    git add .
                    git commit -m "Pipeline: update release image tag to ${RELEASE_TAG}"
                    git push origin main
                """
            }
        }
    }
}
