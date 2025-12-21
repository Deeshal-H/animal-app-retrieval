# Animal Image Retrieval
<br/>

## Objective
<br/>

## Deployment Options:

### 1. <em>Helm</em>

```sh
helm install animal-image-app animal-image-app --namespace [NAMESPACE]
```
The environment variables need to be updated in the `.env.secret` section of the `values.yaml` file. Please see further below for the [environment variables](#env_var).

Once the helm chart is deployed:\
To access the application from a host with kubernetes, run the following command:

```sh
kubectl --namespace [NAMESPACE] port-forward service/animal-image-app 5000:5000
```
The application with then be available on http://127.0.0.1:5000 on the host.

If using minikube, run the following command:

```sh
minikube service animal-image-app --url
```

The above will provide a url in the format http://127.0.0.1:[EPHEMERAL_PORT] where the [EPHEMERAL_PORT] will be output by the minikube command.
<br/><br/>

### 2. <em>Docker</em>

```sh
docker run --name animal-image-app -p 5000:5000 --env-file [ENVIRONMENT_VARIABLES_FILE_PATH] deeshal/animal-image-app:0.1
```
Please see below for the required [environment variables](#env_var).
<br/><br/>

<a id="env_var"></a>
### Required Environment Variables
The environment variables file path must contain the following items:

| Key | Value |
| - | - |
| ZEEBE_REST_ADDRESS | The address of the REST API of the SaaS cluster to connect to. |
| CAMUNDA_TOKEN_AUDIENCE | The audience for which the token should be valid. |
| CAMUNDA_CLIENT_ID | The client ID used to request an access token from the authorization server. |
| CAMUNDA_CLIENT_SECRET | The client secret used to request an access token from the authorization server. |
| CAMUNDA_OAUTH_URL | The URL of the authorization server from which the access token can be requested. |

