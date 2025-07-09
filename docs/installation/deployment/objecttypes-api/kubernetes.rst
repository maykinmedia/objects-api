.. _deployment_objecttypes_kubernetes:

==========
Kubernetes
==========

Here you can find a reference implementation of the Objecttypes API deployment for
a Kubernetes cluster using `Helm`_.

This Helm chart installs the Objecttypes API and is dependent on a PostgreSQL
database, installed using a `subchart`_.

.. warning:: The default settings are unsafe and should only be used for
   development purposes. Configure proper secrets, enable persistence, add
   certificates before using in production.


Installation
============

Install the Helm chart with following commands:

.. code:: shell

   helm repo add maykinmedia https://maykinmedia.github.io/charts/
   helm search repo maykinmedia
   helm install my-release maykinmedia/objecttypen


Use Kubernetes CLI to monitor the status of deployment:

.. code:: shell

   kubectl get pods


If the Ingress is not configured you can use `port-forward` to check the status
of the application:

.. code:: shell

   export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=objecttypes,app.kubernetes.io/instance=objecttypes" -o jsonpath="{.items[0].metadata.name}")
   export CONTAINER_PORT=$(kubectl get pod --namespace default $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")
   echo "Visit http://127.0.0.1:8080 to use your application"
   kubectl --namespace default port-forward $POD_NAME 8080:$CONTAINER_PORT

.. _`Helm`: https://helm.sh/
.. _`subchart`: https://github.com/bitnami/charts/tree/master/bitnami/postgresql
