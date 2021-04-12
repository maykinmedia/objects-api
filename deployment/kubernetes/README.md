# Objects chart

Here you can find a reference implementation of the Objects API deployment for
a Kubernetes cluster using [Helm](https://helm.sh/).

This Helm chart installs the Objects API and is dependent on a [PostgreSQL](https://github.com/bitnami/charts/tree/master/bitnami/postgresql)
database, installed using a subchart.

:warning: The default settings are unsafe and should only be used for development purposes.
Configure proper secrets, enable persistence, add certificates before using in production.

## Installation

Install the Helm chart with following commands:

```bash
cd deployment/kubernetes/objects
helm dependency build .
helm install objects .
```

Use Kubernetes CLI to monitor the status of deployment:
```bash
kubectl get pods
```

If the Ingress is not configured you can use `port-forward` to check the status of the application:
```bash
export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=objects,app.kubernetes.io/instance=objects" -o jsonpath="{.items[0].metadata.name}")
export CONTAINER_PORT=$(kubectl get pod --namespace default $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")
echo "Visit http://127.0.0.1:8080 to use your application"
kubectl --namespace default port-forward $POD_NAME 8080:$CONTAINER_PORT
```
