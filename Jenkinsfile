node() {
    sh 'env | sort'
    stage('build') {
        checkout scm
        def img = docker.build('tsampi/tsampi-server', '.')
       img.push('latest')

    }
}
