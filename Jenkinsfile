pipeline {
    agent {
        docker {
            image 'python:3.11'
            args '-u root:root'
        }
    }

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
                        echo "Logging in to Docker Hub..."
                        sh """
                            echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin
                        """

                        if (env.BRANCH_NAME ==~ /PR-.*/) {
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

                            RELEASE_TAG="${BUILD_NUMBER}"

                            sh """
                                docker buildx create --use || true
                                docker buildx build \
                                    --platform linux/amd64 \
                                    -t ${RELEASE_REPO}:${RELEASE_TAG} \
                                    -t ${RELEASE_REPO}:latest \
                                    --push \
                                    app
                            """

                            env.RELEASE_TAG = RELEASE_TAG
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
                    rm -rf ${GITOPS_REPO}
                    git clone ${GITOPS_URL} ${GITOPS_REPO}

                    sed -i 's/tag: .*/tag: "${RELEASE_TAG}"/' \
                        ${GITOPS_REPO}/charts/fastapi-app/values.yaml

                    cd ${GITOPS_REPO}
                    git config user.email "modusmitch@gmail.com"
                    git config user.name "mmichel122"
                    git add .
                    git commit -m "Update release image tag to ${RELEASE_TAG}"
                    git push origin main
                """
            }
        }
    }
}
