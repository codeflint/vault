# Vault

**Maintainer: Ankit Bahuguna**

Vault is the standard secret store and encryption/decryption service. The standard backend is consul.

### General Information

* `Consul` is used as a backend for storage. It will be deployed in High Availability.

* The `transit` backend from vault is used as a cryptographic service.

* Each service which requires authentication with Vault needs to register as an `AppRole` first.

* The production systems will be monitored for ssh access and deployment, and each ssh access will trigger an email broadacast to key individuals to verify the legitimate access. The individual who wants to deploy stuff in production thus needs to just verify the members in the #deepframe channel before hand.

* By default vault is sealed and is required to be unsealed once to use. This is done by using a secret key split between n-individuals. So at any given point if the vault server restarts or we need to restart the service the n-individual keys are required to unseal it. The generation of these unseal keys happens once, when an admin user initializes vault.

* Official Docker images are used for deploying consul and vault in HA mode. 

* This project provides deployment of infrastructure and sample test code for testing vault's use case for Codeflint.

### Run Instructions [TESTING MODE] 

* In the docker-compose file we define three services. They are:
    - Vault
    - Consul (used as a storage backend for Vault)
    - bash_test (Test Image which gives bash access to Consul and Vault)

* To run the project one needs to set an environment variable with the IP address of the local machine where vault and consul are running.

        export LOCAL_IP=10.10.25.189
  
  Note: If testing locally, **DO NOT** use `localhost` here instead use the actual IP of the machine.

* Build the project using Docker-Compose: 
        
        docker-compose -f docker-compose-test.yml build

* Start the services: 
        
        docker-compose -f docker-compose-test.yml up -d

* Once all services have started. Login to the bash console using the bash_test image.
        
        docker exec -it bash.test bash

* Note: We wil use the bash_test console to seal/unseal, test and verify the status of vault. Also we monitor the logs 
  for consul to check if the data is successfully written to consul storage backend.
    ``` 
    // Verify Consul Members 
    root@df36f20c20a5:/# consul members
    Node          Address          Status  Type    Build  Protocol  DC   Segment
    f47026c1a578  172.21.0.4:9301  alive   server  0.9.0  2         dc1  <all>
    ```
    
    ```
    // Verify Vault Status
    root@df36f20c20a5:/# vault status
    Error checking seal status: Error making API request.
    
    URL: GET http://192.168.2.100:9200/v1/sys/seal-status
    Code: 400. Errors:
    
    * server is not yet initialized
    ```
* For the first time use, Vault needs to be Initialized. Additionally, Vault is in a sealed state, thus the above message is correct. 
So one needs to first initialize it unseal it.
    
    ```bash
    root@df36f20c20a5:/# vault init
    Unseal Key 1: U7HGQVZu2oKZnsReWfv+cJmd+VjPH5jIZwg2MprCPsdU
    Unseal Key 2: zoBj10RGIOnWIAD6Hjvtap2H22HW0ao7VpnSsd6Mcdpf
    Unseal Key 3: 3jWVJ6rzjk9Q6pnHF3HJorM+3c6NEdB/tFZITN2cKdZj
    Unseal Key 4: 7zhGh8Mf5g3KNUH7m60RpFCuyqu1w7sWxUNQvLTvg11+
    Unseal Key 5: 9NKDXI9+iLQVRXTGDjwoewfE38ye94udiXrfpxRrM5DQ
    Initial Root Token: 0875ec91-c4f7-8c90-1449-b26213dd714c
    
    Vault initialized with 5 keys and a key threshold of 3. Please
    securely distribute the above keys. When the vault is re-sealed,
    restarted, or stopped, you must provide at least 3 of these keys
    to unseal it again.
    
    Vault does not store the master key. Without at least 3 keys,
    your vault will remain permanently sealed.
    ```
* Unseal Vault
    One needs to provide three of the above 5 Unseal Keys which were generated during initialization.

    ```bash
    root@df36f20c20a5:/# vault unseal
    Key (will be hidden):
    Sealed: true
    Key Shares: 5
    Key Threshold: 3
    Unseal Progress: 1
    Unseal Nonce: 1c755c5c-ae21-b4fb-7122-9f1edcf40e5c

    root@df36f20c20a5:/# vault unseal
    Key (will be hidden):
    Sealed: true
    Key Shares: 5
    Key Threshold: 3
    Unseal Progress: 2
    Unseal Nonce: 1c755c5c-ae21-b4fb-7122-9f1edcf40e5c

    root@df36f20c20a5:/# vault unseal
    Key (will be hidden):
    Sealed: false
    Key Shares: 5
    Key Threshold: 3
    Unseal Progress: 0
    Unseal Nonce:
    
    ```
    `Sealed: false` means Vault is now unsealed. Now Vault is ready to use.
    
*  Authenticate with Vault using the Inital Root Token, set the same as env variable "VAULT_TOKEN" 
    
    ```bash
    root@df36f20c20a5:/# export VAULT_TOKEN=0875ec91-c4f7-8c90-1449-b26213dd714c
    ```    
    Note: In production, we **WON'T** use the root token, instead we will create APP_ROLES.
    
*   Test the vault authentication by writing some secrets.
    ```bash
    root@df36f20c20a5:/# vault write secret/admin email=abc@abc.com password=12345
    Success! Data written to: secret/admin
    root@df36f20c20a5:/# vault write secret/admin123 email=abc@abc.com password=12345
    Success! Data written to: secret/admin123
    root@df36f20c20a5:/# vault write secret/admin1234 email=abc@abc.com password=12345
    Success! Data written to: secret/admin1234  
    ```    
### Consul Logs and UI

* Conusl UI runs on the LOCAL_IP:9500  
    
    `Consul UI: http://10.10.25.189:9500`

* Consul logs can be monitored to check if the data is successfully written to consul.

    ```bash
    // Invoking : Writing to Consul 
    root@df36f20c20a5:/# vault write secret/admin1231 email=abc@abc.com password=12345
    Success! Data written to: secret/admin1231
    
  // Consul Server Logs
    consul.server |     2017/10/09 00:47:50 [DEBUG] http: Request PUT /v1/session/renew/2e025e62-7c39-da87-9bc9-a1eb9afde898 (113.764µs) from=172.21.0.1:52984
    consul.server |     2017/10/09 00:47:50 [DEBUG] http: Request GET /v1/kv/vault/logical/34b13b8f-efe7-f8ad-df3d-a8c3bbb64c5c/admin1231 (50.939µs) from=172.21.0.1:52984
    consul.server |     2017/10/09 00:47:50 [DEBUG] http: Request PUT /v1/kv/vault/logical/34b13b8f-efe7-f8ad-df3d-a8c3bbb64c5c/admin1231 (9.667571ms) from=172.21.0.1:52984
    consul.server |     2017/10/09 00:47:53 [DEBUG] agent: Check 'vault::80:vault-sealed-check' status is now passing
    consul.server |     2017/10/09 00:47:53 [DEBUG] agent: Service 'vault::80' in sync
    consul.server |     2017/10/09 00:47:53 [DEBUG] agent: Check 'vault::80:vault-sealed-check' in sync
    consul.server |     2017/10/09 00:47:53 [DEBUG] agent: Node info in sync
    consul.server |     2017/10/09 00:47:53 [DEBUG] http: Request PUT /v1/agent/check/pass/vault::80:vault-sealed-check?note=Vault+Unsealed (472.737µs) from=172.21.0.1:52984
    ```

### Transit Backend
* To enable the transit backend on Vault, it needs to be mounted. Unlike the `kv` backend, `transit` backend is required to be mounted at first before use.

    ```bash
    root@df36f20c20a5:/# vault mount transit
    Successfully mounted 'transit' at 'transit'!
    
    // Consul Logs 
    consul.server |     2017/10/09 01:26:06 [DEBUG] http: Request PUT /v1/kv/vault/core/mounts (9.911286ms) from=172.21.0.1:52984
    consul.server |     2017/10/09 01:26:06 [DEBUG] http: Request PUT /v1/kv/vault/core/local-mounts (8.714912ms) from=172.21.0.1:52984
    vault.server | 2017/10/09 01:26:06.245771 [INFO ] core: successful mount: path=transit/ type=transit
    consul.server |     2017/10/09 01:26:06 [DEBUG] http: Request PUT /v1/session/renew/2e025e62-7c39-da87-9bc9-a1eb9afde898 (124.552µs) from=172.21.0.1:52984
    consul.server |     2017/10/09 01:26:07 [DEBUG] agent: Check 'vault::80:vault-sealed-check' status is now passing
    ```
* Create a named encryption Key. A named key is used so that many different applications can use the transit backend with independent keys.
    
    ```bash
    // Creating named encryption key: user_id_1
    root@df36f20c20a5:/# vault write -f transit/keys/user_id_1
    Success! Data written to: transit/keys/user_id_1
    ```
   
   Inspect details of the named encryption key: user_id_1
   
   ```bash
    root@df36f20c20a5:/# vault read transit/keys/user_id_1
    Key                   	Value
    ---                   	-----
    deletion_allowed      	false
    derived               	false
    exportable            	false
    keys                  	map[1:1507512584]
    latest_version        	1
    min_decryption_version	1
    min_encryption_version	0
    name                  	user_id_1
    supports_decryption   	true
    supports_derivation   	true
    supports_encryption   	true
    supports_signing      	false
    type                  	aes256-gcm96
    ```
* **Encrypt** plain text, using named encryption Key: user_id_1
    
    ```bash
    root@df36f20c20a5:/# echo -n "Welcome to codeflint" | base64 | vault write transit/encrypt/user_id_1 plaintext=-
    Key       	Value
    ---       	-----
    ciphertext	vault:v1:ZYWFBW04K9n++r5uuART+pK9/WTgKGkyr25FI4LIPI3lY79mXsx11fhTjnvSoA==

    ```
    **Note:** The encryption endpoint expects the plaintext to be provided as a base64 encoded strings, so we must first 
    convert it. Vault does not store the plaintext or the ciphertext, but only handles it in transit for processing. 
    The application is free to store the ciphertext in a database or file at rest.

* **Decrypt** cipher text back to plain text
    ```bash
    vault write transit/decrypt/user_id_1 ciphertext=vault:v1:ZYWFBW04K9n++r5uuART+pK9/WTgKGkyr25FI4LIPI3lY79mXsx11fhTjnvSoA==
    Key      	Value
    ---      	-----
    plaintext	V2VsY29tZSB0byBHbGltcHNl
    
    root@df36f20c20a5:/# echo "V2VsY29tZSB0byBHbGltcHNl" | base64 -d
    Welcome to codeflint    
    ```
* Note: Using ACLs, it is possible to restrict using the transit backend such that trusted operators can manage the
 named keys, and applications can only encrypt or decrypt using the named keys they need access to.

### AppRole Authentication
* **Adding a Custom Policy:** By default app has only access to it's own access key. In order to be able to get secrets and transition endpoints we have to define custom policy.

    Creating policy file (**@TODO:** add this as a file to repository and transfer to docker container on setup):
    ```
    echo "path "secret/*" {
      capabilities = ["read"]
    }
    path "transit/*" {
      capabilities = ["create", "update"]
    }" > orchestra-policy.hcl
    ```
    
    Creating custom policy:
    ```
    vault write sys/policy/orchestra rules=@orchestra-policy.hcl
    ```


* **Enable AppRole Auth. and Adding new AppRole** (**!Note**: this app settings are only for dev puropses, as the token ttl is 30 days and has unlimited uses)
    ```
    vault auth-enable approle
    vault write auth/approle/role/orchestra secret_id_ttl=43200m token_num_uses=0 token_ttl=43200m token_max_ttl=43200m secret_id_num_uses=0 policies="default,orchestra"
    ```
* **Getting Access Credentials**
    ```
    vault read auth/approle/role/orchestra/role-id
    vault write -f auth/approle/role/orchestra/secret-id
    ```
    * Note: second command will overwrite previous secret-id

### Keygen - Consul

Generates a key which is used to encrypt the internal communication over gossip betweeen consul cluster nodes.

```bash
root@10a3cdd666db:/# consul keygen
yEp46J7We7YQDK0lJTNylw==
```
---

### PRODUCTION DEPLOYMENT

#### Vault with Distributed Consul in High Availability

```
TL;DR Version
-------------
* ACCESS VAULT : 10.10.25.49 (vault-consul-0) Port: 9200
* ACCESS CONSUL : 10.10.25.49 (vault-consul-0) Port: 9500
* On 10.10.25.49, run:
    $ docker run -it -e CONSUL_HTTP_ADDR=10.10.48.150:9500 
                     -e VAULT_ADDR=http://10.10.48.150:9200 
                     vault_bash_test /bin/bash
This starts a test container which can be used to interact with Vault.
* The vault needs to be Unsealed each time the machine is restarted. There are in total 5 unseal keys out of which 
three are needed at the unseal time. 
```

* There are three instances: vault-consul-0: "10.10.25.49",  vault-consul-1: "10.10.18.147", vault-consul-2: "10.10.31.171"
which are the HA backend for consul-vault. Each machine with said name on AWS has the following role:
    * vault-consul-0 `["10.10.25.49"]`: Vault (Transit Backend) + consul-server (Also for Initial Bootstrapping) + private:us-east-1a - t2.xlarge
    * vault-consul-1 `["10.10.18.147"]` : consul-server + private:us-east-1a - t2.micro
    * vault-consul-2 `["10.10.31.171"]`: consul-server + private:us-east-1a - t2.micro 



* An additional 10 GB EBS drive (SSD; encrypted at rest) to each of the instances for data storage. Prepare to use EBS drive on each machine:

```bash

$ sudo mkfs -t ext4 /dev/xvdb
$ sudo mkdir /ebs
$ sudo mount /dev/xvdb /ebs
$ sudo cp /etc/fstab /etc/fstab.orig
$ echo '/dev/xvdb /ebs ext4 rw,noatime,nodiratime,nofail,discard 0 0' | sudo tee --append /etc/fstab > /dev/null
```
 
 
 
 * Push code to the machine (in same order)
```bash
$ pwd
/home/ubuntu
# Test branch : distributed-consul-vault
$ git clone https://github.com/deepframe/vault.git ~/vault # by default checks out master
```

* Export the `LOCAL_IP` environment variable (in same order). Run each commands on its  respective machines as per their ip.

```bash
# vault-consul-0: 10.10.25.49
$ export LOCAL_IP=10.10.25.49

# vault-consul-1:10.10.18.147
$ export LOCAL_IP=10.10.18.147

# vault-consul-2: 10.10.31.171
$ export LOCAL_IP=10.10.31.171
```

* Build containers
```bash
# vault-consul-0: 10.10.25.49
$ cd ~/vault/ && docker-compose -f docker-compose-0.yml build

# vault-consul-1:10.10.18.147
$ cd ~/vault/ && docker-compose -f docker-compose-1.yml build

# vault-consul-2: 10.10.31.171
$ cd ~/vault/ && docker-compose -f docker-compose-2.yml build
```

* Install additional linux packages [htop and tmux]

```bash
$ sudo apt-get install -y htop tmux
```

* Start Consul Containers for the Cluster Setup in the following strict order. Advise: Run each of these in a separate tmux session.

    * To being with, Start consul bootstrap container.
         ```bash
         # vault-consul-0: 10.10.25.49
         $ docker-compose -f docker-compose-0.yml up consul-bootstrap
         ```
    * Then start rest of the consul server containers:
        ```bash
        # vault-consul-1:10.10.18.147
        $ docker-compose -f docker-compose-1.yml up -d consul-1
        
        # vault-consul-2: 10.10.31.171
        $ docker-compose -f docker-compose-2.yml up -d consul-2
        ```
    * Finally press CMD+C or Ctrl + C in terminal to stop the bootstrap container and start the consul-0 containter 
    on the same machine.
        ```bash
        # vault-consul-0: 10.10.25.49
        $ docker-compose -f docker-compose-0.yml up -d consul-0
        ```
    * Consul UI: **TODO** (Currently inside a Private Subnet, thus need to make sure we have a VPN)

    * Start the Vault container on vault-consul-0 instance.
        ```bash
        $ docker-compose -f docker-compose-0.yml up vault-0
    
        ```
    * Start the client container for Accessing Vault
        ```bash
        # vault-consul-0: 10.10.25.49
        $ docker run -it -e CONSUL_HTTP_ADDR=10.10.48.150:9500 -e VAULT_ADDR=http://10.10.48.150:9200 vault_bash_test /bin/bash
        ```    
    Note: Once the prompt begin, the start the process of vault status check, initialization and unsealing as shown before.
    
    * Verify Vault is running in HA after unsealing:
        ```bash
        root@6366d93ddf6b:/# vault status
        Sealed: false
        Key Shares: 5
        Key Threshold: 3
        Unseal Progress: 0
        Unseal Nonce:
        Version: 0.8.3
        Cluster Name: vault-cluster-f1b391b3
        Cluster ID: 09bd25f1-a484-9509-ee2d-61222fe247df
        
        High-Availability Enabled: true
                Mode: active
                Leader Cluster Address: https://10.10.25.49:444
        ```    
    * Note: The `transit` backend has been mounted on the vault instance (10.10.25.49), by using the bash_test container.  
    * System has been tested by:
        * Deleting all the containers one by one. And checking for recovery.
        * Transit and Secret Writing into Vault has been also tested.
        * Machine restart requires a vault unseal
        
    
    
