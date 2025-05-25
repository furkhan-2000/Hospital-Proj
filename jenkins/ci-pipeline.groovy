pipeline {
    agent any
    environment {
        SONAR_HOME = tool 'sonar'
    }
    stages {
        stage('cleaning') {
            steps {
                cleanWs()
            }
        }
        stage('cloning') {
            steps {
                git url: 'https://github.com/furkhan-2000/Hospital-Proj', branch: 'main'
            }
        }
        stage('Dynamic Tagging') {
            steps {
                script {
                    def commitHash = sh(
                        script: "git rev-parse --short HEAD",
                        returnStdout: true
                    ).trim()
                    env.IMAGE_TAG = commitHash
                    echo "Using IMAGE_TAG: ${env.IMAGE_TAG}"
                }
            }
        }
        stage('SONAR ANALYSIS') {
            steps {
                withSonarQubeEnv('sonar') {
                    sh "${SONAR_HOME}/bin/sonar-scanner -Dsonar.projectName=Hospital-Proj -Dsonar.projectKey=Hospital-Proj"
                }
            }
        }
        stage('Sonar Quality Gates') {
            steps {
                timeout(time: 2, unit: 'MINUTES') {
                    script {
                        def qg = waitForQualityGate(abortPipeline: false)
                        if (qg.status != "OK") {
                            error "Quality Gate Failed: ${qg.status}"
                        }
                    }
                }
            }
        }
        stage('owasp') {
            steps {
                timeout(time: 27, unit: 'MINUTES') {
                    retry(2) {
                        dependencyCheck(
                            additionalArguments: '''
                                --scan .
                                --format XML
                                --out ./
                                --prettyPrint 
                            ''',
                            odcInstallation: 'owasp'
                        )
                    }
                    dependencyCheckPublisher pattern: 'dependency-check-report.xml'
                }
            }
        }
        stage('trivy') {
            steps {
                sh "trivy fs ./ --cache-dir ./trivyresult"
                echo "scanning done successfully "
            }
        }
        stage('building') {
            steps {
                sh "docker compose down && docker compose up -d"
                echo "Images build & container started"
            }
        }
        stage('authenticating && Pushing') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerHubCred',
                    usernameVariable: 'DOCKERHUB_USERNAME',
                    passwordVariable: 'DOCKERHUB_PASSWORD'
                )]) {
                    sh '''
                        docker tag hospital-ci-urine-report-check:latest ${DOCKERHUB_USERNAME}/shark:urine-${IMAGE_TAG}
                        docker tag hospital-ci-blood-report-check:latest ${DOCKERHUB_USERNAME}/shark:blood-${IMAGE_TAG}
                        docker login -u ${DOCKERHUB_USERNAME} -p ${DOCKERHUB_PASSWORD}
                        docker push ${DOCKERHUB_USERNAME}/shark:urine-${IMAGE_TAG}
                        docker push ${DOCKERHUB_USERNAME}/shark:blood-${IMAGE_TAG}
                    '''
                }
            }
        }
    }
    post {
        success {
            build job: "Hospital-CD",
                  parameters: [string(name: 'IMAGE_TAG', value: "${env.IMAGE_TAG}")],
                  wait: false,
                  propagate: false
            echo "CD-Job started successfully for CI pipeline"
        }
        failure {
            mail to: "furkhan2000@icloud.com", 
                 subject: "Pipeline Failed", 
                 body: "Hospital-CI Pipeline build number ${env.BUILD_NUMBER} failed. Please review the console output. ${env.BUILD_URL}"
            echo "mail send successfully for CI pipeline"
        }
    }
}
