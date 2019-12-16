# translation-api-service

## Create 
Build Docker images and push 
```bash
docker build -f translation-api-perf/Dockerfile -t vmalashkov/translation-api-perf .
docker push vmalashkov/translation-api-perf

docker build -f translation-api/Dockerfile -t vmalashkov/translation-api-service .
docker push vmalashkov/translation-api-service
```
Run 
```bash
cd infrastructure
terraform apply
```

Then get kubeconfig file 
```bash
aws eks update-kubeconfig --name translation-api-cluster --kubeconfig config.yaml
export KUBECONFIG=${PWD}/config.yaml
```

Then you need to init Helm
```bash
kubectl apply -f ./infrastructure/rbac.yaml
helm init --service-account tiller
```

Install API service
```bash
helm install -n translation-api ./chart
```

Install locust service
```bash
helm install -n locust \
    --set service.type=LoadBalancer \
    --set master.config.target-host=http://translation-api-lb:8080 \
    --set image.repository=vmalashkov/translation-api-perf \
    --set image.tag=latest \
    --set worker.replicaCount=3 \
    --set worker.config.locust-script=/usr/src/app/test.py \
    stable/locust
```

Install dashboard
```bash
helm install -n dashboard \
    --set rbac.clusterAdminRole=true \
    --set enableSkipLogin=true \
    --namespace kube-system \
    --set fullnameOverride="dashboard" \
    stable/kubernetes-dashboard
```

UI is at 
`http://localhost:8001/api/v1/namespaces/kube-system/services/https:dashboard:https/proxy`

To login into dashboard use token 
```bash
kubectl get secrets --namespace kube-system
```

Find something starting with `dashboard-token-`
And then 
```bash
 kubectl describe secret dashboard-token-<ID> --namespace kube-system
```

Install metrics server 
```bash
helm install stable/metrics-server \
    --name metrics-server \
    --namespace metrics
```

Install autoscaler 
```bash
helm install --name autoscaler \
    --set autoDiscovery.clusterName=translation-api-cluster \
    --set autoDiscovery.enabled=true \
    --set awsRegion=eu-central-1 \
    --set cloudProvider=aws \
    --set rbac.create=true \
    stable/cluster-autoscaler
```

## Destroy 

Delete charts
```bash
helm delete --purge locust
helm delete --purge translation-api
```

Destroy cluster
```bash
terraform destroy
```

## Vegeta performance

For local testing
```
echo 'GET http://localhost:8080/translate?text=hello' | vegeta -cpus 4 attack -rate 3000 -duration 20s -timeout 1s | vegeta report
```

For AWS cloud
```bash
echo 'GET http://<elb endpoint>:8080/translate?text=hello' | vegeta -cpus 4 attack -rate 1000 -duration 5s -timeout 1s | vegeta report
```