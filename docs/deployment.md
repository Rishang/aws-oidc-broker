### Kubernetes with DevSpace

#### Prerequisites

  - [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
  - [kube-login](https://github.com/int128/kubelogin)
  - [Valid Kubeconfig at ~/.kube/config](https://gitlab.openxcell.dev/-/snippets/22/raw/main/config)
  - [devspace cli](https://devspace.sh/cli/docs/quickstart)
  - Ensure you are logged in to docker registry and have necessary permissions to push images to the project
  
    ```bash
    docker login
    ```


#### Base64 encode the Keycloak Client Secret and Copy the Output
  
  ```bash
  echo <keycloak-client-secret> | base64
  ```

#### Update `secret.yaml` with Base64 Encoded Keycloak Client Secret Copied from Previous Step
  
    ```diff
    apiVersion: v1
    kind: Secret
    metadata:
        name: keycloak-client
    type: Opaque
    data:
    -  KEYCLOAK_CLIENT_SECRET: base64-data
    +  KEYCLOAK_CLIENT_SECRET: <base64-encoded-client-secret> 
    ```
#### Create Kubernetes Secret
  
  ```bash
  kubectl apply -f secret.yml -n devops
  ```

#### Set correct values for Environment variables in `devspace.yaml`
  
  `KEYCLOAK_CLIENT_ID`

  `KEYCLOAK_ISSUER`

  `APP_SECRET`

  `TITLE`

#### Deploy
  
  ```bash
  devspace use namespace devops
  devspace deploy
  ```