node() {
    stage('build') {
        checkout scm
        sh "docker-compose build"
    }
    stage('test') {

        sh "docker-compose server test_coverage"

    }
}
