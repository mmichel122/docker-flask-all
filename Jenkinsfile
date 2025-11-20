pipeline {
    agent any

    environment {
        DEV_REPO    = "mmocker06/fastapi-app-dev"
        RELEASE_REPO = "mmocker06/fastapi-app"
        GITOPS_REPO = "/tmp/gitops"
        GITOPS_URL  = "https://github.com/mmichel122/argocd-k8s-automation.git"
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
                    docker build -t app:local .
                """
            }
        }

        stage('Push Image') {
            steps {
                withCredentials([string(credentialsId: 'dockerhub-token', variable: 'TOKEN')]) {
                    script {

                        if (env.BRANCH_NAME ==~ /PR-.*/) {
                            echo "Building for DEV..."
                            DEV_TAG="pr-${CHANGE_ID}"

                            sh """
                                echo "$TOKEN" | docker login -u mmocker06 --password-stdin
                                docker tag app:local ${DEV_REPO}:${DEV_TAG}
                                docker push ${DEV_REPO}:${DEV_TAG}
                            """

                        } else if (env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'master') {
                            echo "Building for RELEASE..."
                            RELEASE_TAG="${BUILD_NUMBER}"

                            sh """
                                echo "$TOKEN" | docker login -u mmocker06 --password-stdin
                                docker tag app:local ${RELEASE_REPO}:${RELEASE_TAG}
                                docker push ${RELEASE_REPO}:${RELEASE_TAG}
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

                    sed -i 's/tag: .*/tag: "${RELEASE_TAG}"/' ${GITOPS_REPO}/charts/fastapi-app/values.yaml

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
