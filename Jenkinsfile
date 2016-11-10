node() {
    stage('build') {
        sh 'env | sort'
        sh 'docker-compose build'
    }
    stage('test') {
        sh 'docker-compose server manage test
    }
}
