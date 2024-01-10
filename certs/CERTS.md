# Creating Self Signed CA certificates
In this application setup, we will generate a self-signed CA certificate that we will use to create on-transit data encryption SSL certificates for all servers in the cluster.

In a production environment, this certificate should be obtained from a reputable issuer. The certificate will also be used to create client-side SSL certificates for on-transit data encryption. Thus, a client can only communicate with the server if it has an SSL certificate signed using the given CA.


## SSL 101

To obtain an SSL certificate, one needs to send a Certificate Signing Request (CSR) to Certificate Authorities such as Verisign or GoDaddy. The CA provides an SSL certificate signed using their root certificate and private key.

For a self-signed SSL certificate, we need to act as a CA and provision our own CA root certificate and private key. Using this combination, we can generate any number of SSL certificates to secure communication between servers in the cluster.

 ## Creating a self signed CA key and certificate

 ### Generating CA Private key

Write the following command to generate an RSA private key. If asked for a passphrase, provide one as it is a security feature. In the event your private key is compromised, it cannot be used to generate a CA certificate or SSL certificates.

 ```bash
 openssl genrsa -des3 -out ca.key 2048
 ```

 ### Generating CA certificate

 ```bash
openssl req -x509 -new -node -key ca.key -sha256 -days 365 -out ca.pem
 ```

 with the two files we can comfortably sign both server and client certificates


 ### NOTE

Since our CA key has a passphrase (which should be kept secret), running the Ansible playbook would cause the process to halt, as SSL certificate creation on the remote servers would prompt you to enter the passphrase.

We need a secure way to pass the passphrase to the Ansible process generating the SSL certificates on the remote servers. To do that, we will utilize an amazing Ansible tool called ansible-vault. This tool, as the name suggests, is used to store secret information that is required during infrastructure deployment but is too risky to expose to the public.

As such, we need to encrypt the CA key passphrase.

 #### Encrypting the CA private key phrase

 ```bash
 ansible-vault encrypt_string --name 'ca_key_passphrase' 'some top secrete passphrase'
 ```

 the above command should produce an output as shown below

 ```yaml
 ca_certificate_passphrase: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          31313539633939626435373761....
 
 
 ```

 Copy the above output and add it to the vars file belonging to the collect task as:

 ```yaml
 ca_certificate_passphrase: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          31313539633939626435373....
 ```

 update the task on the role that requires the certificate to create an ssl certificate as

 ```yaml
 - name: Generate Redis Server Certificate and Keys
  tags: server, certgen
  shell: >
    cd /tmp && openssl genrsa -out redis.key 2048 && \
    openssl req -new -sha256 -key redis.key \
    -subj "/O=RedisLabs/CN=Production Server Certificate" | \
    openssl x509 -req -sha256 \
    -CA {{ ca_certificate_destination }} \
    -CAkey {{ ca_key_destination }} -passin pass:{{ ca_certificate_passphrase }} \
    -CAcreateserial \
    -days 365 \
    -out redis.crt && \
    mv redis.key /etc/ssl/private/ && \
    mv redis.crt /etc/ssl/
 
 ```

 Notice we have requested ansible to pass the passphrase from the vault using ` -passin pass:{{ ca_key_passphrase }}` this will pass the key to the process securely.


 To run the playbook we need to use the flag `--ask-vault-pass` we will be requested for the vault password we set.