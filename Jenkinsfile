pipeline {
    agent any

    environment {
        DEV_REPO       = "mmocker06/fastapi-app-dev"
        RELEASE_REPO   = "mmocker06/fastapi-app"
        GITOPS_REPO    = "/tmp/gitops"
        GITOPS_URL     = "https://github.com/mmichel122/argocd-k8s-automation.git"
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
                        echo "Logging into Docker Hub…"

                        sh """
                            echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin
                        """

                        // PRs → DEV image :latest
                        if (env.BRANCH_NAME ==~ /PR-.*/) {
                            echo "Building DEV image…"

                            sh """
                                docker buildx create --use || true

                                docker buildx build \
                                    --platform linux/amd64 \
                                    -t ${DEV_REPO}:latest \
                                    --push \
                                    app
                            """
                        }

                        // main/master → RELEASE image :stable + :latest
                        else if (env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'master') {
                            echo "Building RELEASE image…"

                            sh """
                                docker buildx create --use || true

                                docker buildx build \
                                    --platform linux/amd64 \
                                    -t ${RELEASE_REPO}:stable \
                                    -t ${RELEASE_REPO}:latest \
                                    --push \
                                    app
                            """

                            env.RELEASE_TAG = "stable"
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
