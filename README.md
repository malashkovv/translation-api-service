# translation-api-service

## Local setup

Tested on Ubuntu 20.04 LTS with Nvidia driver 460 (CUDA 11.2).

## Kubernetes setup

### EKS

#### Create

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

Run proxy to get access to dashboard:
```bash
kubectl proxy
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

Redeploy API:
```bash
helm upgrade translation-api ./chart --install --force --reset-values --set image.pullPolicy=Always
```

#### Destroy

Delete charts
```bash
helm ls --all --short | xargs -L1 helm delete --purge
```

Destroy cluster
```bash
terraform destroy
```

### microk8s

#### Create

```bash
microk8s enable dashboard gpu dns helm registry
```

```bash
microk8s.helm init
```

Note: you need to add `microk8s` before each `helm`, `kubectl` or other commands available in `microk8s` 

Open separate tab to port-forward dashboard
```bash
microk8s kubectl port-forward -n kube-system service/kubernetes-dashboard 10443:443
```

It will be available at `https://localhost:10443`

To login into dashboard use token
```bash
token=$(microk8s kubectl -n kube-system get secret | grep default-token | cut -d " " -f1)                                       ✔  base Py  23:18:33 
microk8s kubectl -n kube-system describe secret $token
```

Build and push local image into microk8s registry
```bash
docker build -f translation-api/Dockerfile -t localhost:32000/translation-api:dev .
docker push localhost:32000/translation-api:dev
```

Install API service with local image
```bash
microk8s helm install -n translation-api ./chart \
    --set workers.replicaCount=2 \
    --set image.repository=localhost:32000/translation-api \
    --set image.tag=dev
```

#### Destroy

Delete translation api chart
```bash
microk8s helm del --purge translation-api
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

Example report:
```bash
> echo 'GET http://a018dcd6c202611ea8d600a70e5e28fe-201213391.eu-central-1.elb.amazonaws.com:8080/translate?text=hello' | vegeta -cpus 4 attack -rate 2000 -duration 5s -timeout 1s | vegeta report
Requests      [total, rate, throughput]  10000, 2000.23, 1936.70
Duration      [total, attack, wait]      5.078213063s, 4.999413972s, 78.799091ms
Latencies     [mean, 50, 95, 99, max]    69.668173ms, 63.431027ms, 89.035634ms, 207.208686ms, 1.000132776s
Bytes In      [total, mean]              236040, 23.60
Bytes Out     [total, mean]              0, 0.00
Success       [ratio]                    98.35%
Status Codes  [code:count]               0:165  200:9835
```
