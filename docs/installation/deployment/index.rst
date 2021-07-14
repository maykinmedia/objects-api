.. _deployment_index:

Deployment
==========

Both (*Objects* and *Objecttypes*) APIs are containerized applications and can be
deployed to a single server or `Kubernetes`_ cluster. We use `Ansible`_
playbooks for the single server deployment and `Helm`_ chart for
Kubernetes cluster.

The documentation includes installation process and the reference configuration.

.. toctree::
   :maxdepth: 2
   :caption: Deployment

   objects-api/index
   objecttypes-api/index


.. _`Ansible`: https://www.ansible.com/
.. _`Helm`: https://helm.sh/
.. _`Kubernetes`: https://kubernetes.io/
