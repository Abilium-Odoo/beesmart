node {
    
    stage('Git Stage') {
        checkout([$class: 'GitSCM', branches: [[name: '*/main']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: '', url: 'https://github.com/Abilium-Odoo/beesmart.git']]])
    }

    stage('Deploy:Prod') {
        sh('kubectl delete pod -l app=odoo --kubeconfig=/var/lib/jenkins/.kube/beesmart_prod')
    }
}
