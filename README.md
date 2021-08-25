# translation-api-service

## Local setup

Tested on Ubuntu 20.04 LTS with Nvidia driver 460 (CUDA 11.2).

## Kubernetes setup

### EKS

NOTE: This section is outdated as it uses helm 2 and not 3.

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
    --set worker.config.locust-script=/usr/src/app/main.py \
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
helm install --name autoscaler.yaml \
    --set autoDiscovery.clusterName=translation-api-cluster \
    --set autoDiscovery.enabled=true \
    --set awsRegion=eu-central-1 \
    --set cloudProvider=aws \
    --set rbac.create=true \
    stable/cluster-autoscaler.yaml
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

### minikube

Unfortunately, I haven't managed to run `minikube` with GPU enabled, I did not have a spare one. Please,
see official docs on how to enable GPU.

#### Create

Start the cluster
```bash
minikube start
```

Enable addons
```bash
minikube addons enable registry
minikube addons enable helm-tiller
minikube addons enable metrics-server
```

In order to get to the dashboard run in a separate tab
```bash

```

Build and push local image into microk8s registry
```bash
docker build -f translation-api/Dockerfile -t translation-api .
minikube image load translation-api:latest
```

Install API chart
```bash
helm install translation-api ./chart \
    --set workers.gpu=0 \
    --set image.repository=translation-api \
    --set image.tag=latest
```

To access webserver run
```bash
minikube tunnel
```

After that get `EXTERNAL_IP` for a load balancer with the following command
```bash
kubectl get svc
```

Now you can access it at `<EXTERNAL_IP>:80/docs`

Or yu can run
```bash
minikube service translation-api-lb --url
```


Build perf image
```bash
docker build -f translation-api-perf/Dockerfile -t translation-api-perf .
minikube image load translation-api-perf:latest
```

Install locust service
```bash
helm repo add deliveryhero https://charts.deliveryhero.io/

kubectl create configmap loadtest-locustfile --from-file translation-api-perf/main.py

helm install locust deliveryhero/locust \
    --set loadtest.name=loadtest \
    --set loadtest.locust_locustfile_configmap=loadtest-locustfile \
    --set loadtest.locust_host=http://translation-api-lb:80 \
    --set worker.replicas=2
```

#### Destroy

Delete service
```bash
helm del translation-api
helm del locust
```

## Performance tests

### Vegeta

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

## Useful links

* [Locust Helm Chart](https://github.com/deliveryhero/helm-charts/tree/master/stable/locust)
* [Uvicorn Deployment](https://www.uvicorn.org/deployment/)
* [An introduction to Kubernetes](https://www.jeremyjordan.me/kubernetes/amp/)
* [Kubernetes Concepts and Architecture](https://platform9.com/blog/kubernetes-enterprise-chapter-2-kubernetes-architecture-concepts/)
* [Provisioning Kubernetes clusters on AWS with Terraform and EKS](https://learnk8s.io/terraform-eks)
* [EKS GPU worker group using Terraform](https://stackoverflow.com/questions/65774363/eks-gpu-worker-group-using-terraform)
* [Quotes Dataset](https://www.kaggle.com/akmittal/quotes-dataset)
* [Serving ML models with multiple workers linearly adds the RAM's load](https://github.com/tiangolo/fastapi/issues/2425#issuecomment-734790381)
* [PyTorch 101, Part 4: Memory Management and Using Multiple GPUs](https://blog.paperspace.com/pytorch-memory-multi-gpu-debugging/)
