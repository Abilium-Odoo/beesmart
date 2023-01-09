node {
    
    stage('Git Stage') {
        checkout([$class: 'GitSCM', branches: [[name: '*/main']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'jenkins01', url: 'git@github.com:Abilium-Odoo/beesmart.git']]])
    }

    stage('Deploy:Prod') {
        sh('kubectl delete pod -l app=odoo --kubeconfig=/var/lib/jenkins/.kube/beesmart_prod')
    }
}
