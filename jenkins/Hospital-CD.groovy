pipeline {
    agent any

    parameters {
        string(name: 'IMAGE_TAG', defaultValue: '', description: 'this is updated tag from CI')
    }

    environment {
        GIT_REPO    = 'https://github.com/furkhan-2000/Hospital-Proj.git'
        DOCKER_IMAGE = 'furkhan2000/shark'
        DOCKER_TAG  = "${params.IMAGE_TAG}"
    }

    stages {
        stage('Clean Workspace') {
            steps {
                cleanWs()
            }
        }

        stage('Verify Image Tag') {
            steps {
                script {
                    if (!env.DOCKER_TAG?.trim() ) {
                    error "Image form CI not found"
                    }
                    echo "Latest Image found: ${env.DOCKER_TAG}"
                }
            }
        }

        stage('Authenticating && Pushing') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'githubCred',
                    usernameVariable: 'GITHUB_USERNAME',
                    passwordVariable: 'GITHUB_PASSWORD'
                )]) {
                    sh """
                        git clone ${GIT_REPO} k8-hosp
                        cd k8-hosp
                        sed -i "s|image: ${DOCKER_IMAGE}:.*|image: ${DOCKER_IMAGE}:${DOCKER_TAG}|g" k8-hosp/blood-report-k8.yaml
                        sed -i "s|image: ${DOCKER_IMAGE}:.*|image: ${DOCKER_IMAGE}:${DOCKER_TAG}|g" k8-hosp/urine-report-k8.yaml
                        git config user.name "bottle"
                        git config user.email "bottle12@gmail.com"
                        git add k8-hosp/blood-report-k8.yaml k8-hosp/urine-report-k8.yaml
                        git commit -m "Updated image tag to ${DOCKER_TAG} for both blood and urine deployments"
                        git push https://${GITHUB_USERNAME}:${GITHUB_PASSWORD}@github.com/furkhan-2000/Hospital-Proj.git
                    """
                }
            }
        }

        stage('Check Rollout Status') {
            steps {
                script {
                    def bloodStatus = sh(
                        script: "kubectl rollout status deployment/blood --namespace=prod --timeout=90s",
                        returnStatus: true
                    )
                    if (bloodStatus != 0) {
                        echo "Blood deployment rollout failed. Attempting rollback..."
                        sh "kubectl rollout undo deployment/blood --namespace=prod"
                        def bloodRollbackStatus = sh(
                            script: "kubectl rollout status deployment/blood --namespace=prod --timeout=90s",
                            returnStatus: true
                        )
                        if (bloodRollbackStatus != 0) {
                            error "Blood deployment rollback failed; manual intervention required."
                        } else {
                            echo "Blood deployment failed, but rollback succeeded."
                        }
                    } else {
                        echo "Blood deployment is healthy."
                    }

                    def urineStatus = sh(
                        script: "kubectl rollout status deployment/urine --namespace=prod --timeout=90s",
                        returnStatus: true
                    )
                    if (urineStatus != 0) {
                        echo "Urine deployment rollout failed. Attempting rollback..."
                        sh "kubectl rollout undo deployment/urine --namespace=prod"
                        def urineRollbackStatus = sh(
                            script: "kubectl rollout status deployment/urine --namespace=prod --timeout=90s",
                            returnStatus: true
                        )
                        if (urineRollbackStatus != 0) {
                            error "Urine deployment rollback failed; manual intervention required."
                        } else {
                            echo "Urine deployment rollback succeeded."
                        }
                    } else {
                        echo "Urine deployment is healthy."
                    }
                }
            }
        }
    }

    post {
        success {
            mail to: "furkhan2000@icloud.com",
                 subject: "Pipeline Success",
                 body: "Hi team, the pipeline succeeded. Build Number: ${env.BUILD_NUMBER}\nYou can check details at: ${env.BUILD_URL}"
        }
        failure {
            mail to: "furkhan2000@icloud.com",
                 subject: "Pipeline Failed",
                 body: "Hi team, the pipeline failed. Build Number: ${env.BUILD_NUMBER}\nPlease review the logs: ${env.BUILD_URL}"
        }
    }
}
