# Redis Cluster Mode Tutorial with TLS and UCLs Enabled

This tutorial will guide you through the process of setting up a Redis cluster in Cluster mode with both Transport Layer Security (TLS) and User ACLs (UCLs) enabled. We will use Ansible as our automation tool to set up the servers, and the client application will be a Python Flask web app.

## Prerequisites

Before getting started, make sure you have the following:

- Ansible installed on your local machine.
- A set of server machines where Redis will be installed. These servers should have SSH access and meet the minimum system requirements for running Redis.
- A domain name or public IP address for each server.

## Step 1: Setting up the Redis Servers

1. Clone the repository containing the Ansible playbook for Redis cluster setup:


2. Modify the `hosts` file in the repository to include the domain names or IP addresses of your Redis servers.

3. Open the `group_vars/all.yml` file and configure the following variables:

- `redis_cluster_tls_enabled`: Set it to `true` to enable TLS for Redis.
- `redis_cluster_tls_cert_path`: Specify the path to your TLS certificate file.
- `redis_cluster_tls_key_path`: Specify the path to your TLS private key file.
- `redis_cluster_ucls_enabled`: Set it to `true` to enable UCLs for Redis.
- `redis_cluster_ucls_config_path`: Specify the path to your UCLs configuration file.

4. Run the Ansible playbook to set up the Redis servers:

```bash 
ansible-playbook -i hosts playbooks/redis-cluster.yml
```

This playbook will install Redis, configure it for cluster mode, enable TLS, and set up UCLs based on your provided configurations.

5. Verify that the Redis cluster is set up correctly by connecting to one of the Redis nodes and running the `redis-cli` command:

```bash
redis-cli -c -h <redis-node-host> -p <redis-node-port>
```


You should be able to connect to the Redis node and execute Redis commands.

## Step 2: Setting up the Python Flask Web App

1. Run client's setup ansible playbook to set up the flask application

```bash
    ansible-playbook -i clients playbooks/redis-client.yml
```
This will install the flask application as a systemd service


## Setting up the cluster

Once all the nodes are running in cluster mode. now its just a matter of provisioning the cluster. 
This can be done from any computer with access to the node's network having redis-cli client installed.

By default redis prohibits remote access by running in protected-mode. thus this default behavior would prevent use from
provisioning the cluster from a remote computer. thus we can disable this behavior by setting `protected-mode = no`.

The above change makes any of our nodes vulnerable to attacks. to mitigate such we can set up ucl's that limit any user from 
running dangerous commands i.e commands that can change the state of our server. 

Also on top of requiring a signed client certificate and a key to connect to the node, we can request the client to provide some pre-registered password
so as to authenticate. with that set. provisioning the cluster is just a matter of running the command below

```bash
redis-cli --tls --cert /path/to/client/certificate --key /path/to/client/private_key --cacert /path/to/the/ca/cert --cluster create [ipaddess/hostname_to_node:tls_port, ....] --cluster-replicas num_of_replica_per_master

```

with that redis will try to configure a suitable setup given the number of nodes available and the number of replicas required. just agree and the cluster will be provisioned
