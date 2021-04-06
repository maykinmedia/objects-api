.. _deployment_objecttypes_kubernetes:

==========
Kubernetes
==========

Here you can find a reference implementation of Objecttypes deployment in the
Kubernetes cluster via `Helm`_.
This Helm chart installs Objecttypes API and is dependent on `PostgreSQL subchart`_.

.. warning:: The default settings are unsafe and should be used only for
   development purposes. Configure proper secrets, enable persistence, add
   certificates before using in production.


Installation
============

Install the Helm chart with following commands:

.. code:: shell

   cd deployment/kubernetes/objecttypes
   helm dependency build .
   helm install objecttypes .


Use Kubernetes CLI to monitor the status of deployment:

.. code:: shell

   kubectl get pods


If ingress is not configured you can use `port-forward` to check the status of application:

.. code:: shell

   export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=objecttypes,app.kubernetes.io/instance=objecttypes" -o jsonpath="{.items[0].metadata.name}")
   export CONTAINER_PORT=$(kubectl get pod --namespace default $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")
   echo "Visit http://127.0.0.1:8080 to use your application"
   kubectl --namespace default port-forward $POD_NAME 8080:$CONTAINER_PORT

.. _`Helm`: https://helm.sh/
.. _`PostgreSQL subchart`: https://github.com/bitnami/charts/tree/master/bitnami/postgresql
