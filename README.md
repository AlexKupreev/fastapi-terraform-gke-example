# Example FastAPI app in GKE

## FAQ

### What is it?

This is a reworked python API backend from 
great [Full Stack FastAPI PostgreSQL template](https://github.com/tiangolo/full-stack-fastapi-postgresql) 
that is to be deployed to GKE cluster.
The python code was refactored as inspired by awesome [Architecture Patterns with Python](https://www.cosmicpython.com/book/preface.html).
The app aims to implement some of [12 factor app principles](https://12factor.net/) principles.   

Basic features:

* python API backend:
  * FastAPI
  * SQLAlchemy ORM with PostgreSQL DB
  * Cloud Logging integration
  * Cloud Pub/Sub integration (for Cloud Scheduler usage)
* terraform configuration for setting up Google Cloud infrastructure
* helm charts for deployment into GKE
* CI/CD using Cloud Build


### Why is it needed?

* It is a self-educational project - I wanted to understand how terraform, kubernetes and cloud-native approach work.
* Did not find anything similar containing API, architectural approach and cloud native at once.
* This is an easy-to-go thing - follow instructions and get a deployed minimal API in GKE cluster - 
with authentication and simple user management (yes, it really worked on GKE cluster, but was a way **expensive**).


### What is its status?

It is completed in its basic version: 
* HTTP REST API endpoint
* Deployed to GKE minimal cluster
* Pub/Sub pull subscriber listening for Cloud Schedule jobs
* HTTP server and Pub/Sub listener sit within a single container and are managed by supervisord 
  (separate containers would ne more convenient and appropriate for Cloud native approach, 
  but more expensive) 
* Cloud Logging writing logs (a bit confusing that several messages are pushed as errors, 
  that is probably because of supervisord default way of log printing)
* Emailing probably **doesn't work** - it is just a copy-paste from the original repo, not tested it in GKE.
* Sentry and Flower integration **does not work** as well, their configuration should be ignored. 

**Please note:** this configuration is pretty **expensive** for simple pet project apps.


## Requirements

* [Docker](https://www.docker.com/).
* [Docker Compose](https://docs.docker.com/compose/install/).
* [Poetry](https://python-poetry.org/) for Python package and environment management.


## Configuration

Copy `docker/compose/.env.tpl` to `docker/compose/.env` and fill in necessary settings. 

## Backend local development

### Running dev application locally

* Start the stack with Docker Compose:

  ```shell
  docker-compose -f docker/compose/docker-compose.dev.yml up -d
  ```

* Open your browser and interact with these URLs:

  * http://localhost:8888/api/ - backend, JSON based web API based on OpenAPI

  * http://localhost:8888/docs - automatic interactive documentation with Swagger UI (from the OpenAPI backend) 

  * http://localhost:8888/redoc - alternative automatic documentation with ReDoc (from the OpenAPI backend) 


**Note**: The first time starting the stack, it might take a minute for it to be ready. While the backend waits for the database to be ready and configures everything. You can check the logs to monitor it.

To check the logs, run:

```bash
docker-compose logs
```

To check the logs of a specific service, add the name of the service, e.g.:

```bash
docker-compose logs backend
```

To rebuild app container run 

```bash
docker-compose -f docker/compose/docker-compose.dev.yml build
```

Please note, that there is another docker image: `docker/backend.dockerfile` 
and compose configuration: `docker/compose/docker-compose.yml` - they are for production 
(and production running locally).

### General development workflow

1. The dependencies are managed with [Poetry](https://python-poetry.org/), go there and install it.

2. Go to project root and install all the dependencies with:

   ```console
   $ poetry install
   ```

3. Start a shell session with the new environment:

   ```console
   $ poetry shell
   ```

4. Open your editor and make sure your editor uses the environment you just created with Poetry.


### Docker Images

Unlike the original template, that one has two separate dockerfiles and docker-compose configurations:

* `docker/backend.dev.dockerfile` - development configuration with hot reload (compose file: `docker/compose/docker-compose.dev.yml`)
* `docker/backend.dockerfile` - production configuration (compose file: `docker/compose/docker-compose.yml`)

To get inside the container with a `bash` session you can start the stack with:

```console
$ docker-compose up -d
```

and then `exec` inside the running container:

```console
$ docker-compose exec backend bash
```

You should see an output like:

```console
root@7f2607af31c3:/app#
```

that means that you are in a `bash` session inside your container, as a `root` user, under the `/app` directory.


### Testing

To test the app from dev environment go to the project root and run:

```console
$ pytest
```

To run the local tests with coverage reports:

```console
$ pytest --cov=.
```

### Code style and static checks

Run code formatter:

```console
$ black .
```

Run linters:

```console
$ flake8
$ pylint src/
```

Run static type checker:

```console
$ mypy src/
```

### Migrations

As during local development your app directory is mounted as a volume inside the container, you can also run the migrations with `alembic` commands inside the container and the migration code will be in your app directory (instead of being only inside the container). So you can add it to your git repository.

Make sure you create a "revision" of your models and that you "upgrade" your database with that revision every time you change them. As this is what will update the tables in your database. Otherwise, your application will have errors.

* Start an interactive session in the backend container:

```console
$ docker-compose exec backend bash
```

* After changing a model (for example, adding a column), inside the container, create a revision, e.g.:

```console
$ alembic revision --autogenerate -m "Add column last_name to User model"
```

* Commit to the git repository the files generated in the alembic directory.

* After creating the revision, run the migration in the database (this is what will actually change the database):

```console
$ alembic upgrade head
```

If you don't want to start with the default models and want to remove/modify them 
from the beginning without having any previous revision, 
remove the revision files (`.py` Python files) under `./alembic/versions/`. 
Then create a first migration as described above.

After completing the first migration, initial data can be pre-filled using API endpoint:

```
POST %domain:port%/api/v1/basic_utils/test-pubsub/prefill_db
```


## Setting up CI/CD pipeline using Github and GKE

**Note**: I use `project-name-314159` as the project name in Cloud Services. 

### Articles used while setting up the process:

* https://www.padok.fr/en/blog/kubernetes-google-cloud-terraform-cluster
* https://mudrii.medium.com/google-gke-and-sql-with-terraform-294fb840619d
* https://blog.engineering.publicissapient.fr/2020/06/09/39715/
* https://github.com/GoogleCloudPlatform/gke-private-cluster-demo
* https://www.padok.fr/en/blog/kubernetes-google-cloud-platform-app-helm
* https://www.padok.fr/en/blog/kubernetes-gcp-cloud-build
* https://github.com/roma-d/google-cloud-platform-ci-cd-python-app
* https://cloud.google.com/solutions/managing-infrastructure-as-code
* https://dev.to/hedlund/scheduled-google-cloud-functions-using-terraform-and-pub-sub-2i8o

### Setting up infrastructure with Terraform

Assume that project and billing have already been created.

Install SDK and kubectl, then init SDK:

```shell
gcloud init
```

This gcloud configuration has been called [fastapi-gke]. 

Use Terraform to roll out a cluster: 

```shell
wget https://releases.hashicorp.com/terraform/0.14.8/terraform_0.14.8_linux_amd64.zip
unzip terraform_0.14.8_linux_amd64.zip
sudo mv terraform /opt/terraform
sudo ln -s /opt/terraform /usr/local/bin/terraform
```

Enable the Google Cloud APIs that will be used:

```shell
gcloud services enable compute.googleapis.com
gcloud services enable servicenetworking.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable container.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable pubsub.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable appengine.googleapis.com
```

Then create a service account named `terraform-gke`:

```shell
gcloud iam service-accounts create terraform-gke
```

Now grant the necessary roles for our service account to create a GKE cluster and the associated resources:

```shell
gcloud projects add-iam-policy-binding project-name-314159 --member serviceAccount:terraform-gke@project-name-314159.iam.gserviceaccount.com --role roles/container.admin
gcloud projects add-iam-policy-binding project-name-314159 --member serviceAccount:terraform-gke@project-name-314159.iam.gserviceaccount.com --role roles/compute.admin
gcloud projects add-iam-policy-binding project-name-314159 --member serviceAccount:terraform-gke@project-name-314159.iam.gserviceaccount.com --role roles/iam.serviceAccountAdmin
gcloud projects add-iam-policy-binding project-name-314159 --member serviceAccount:terraform-gke@project-name-314159.iam.gserviceaccount.com --role roles/resourcemanager.projectIamAdmin
gcloud projects add-iam-policy-binding project-name-314159 --member serviceAccount:terraform-gke@project-name-314159.iam.gserviceaccount.com --role roles/cloudsql.admin
gcloud projects add-iam-policy-binding project-name-314159 --member serviceAccount:terraform-gke@project-name-314159.iam.gserviceaccount.com --role roles/storage.admin
gcloud projects add-iam-policy-binding project-name-314159 --member serviceAccount:terraform-gke@project-name-314159.iam.gserviceaccount.com --role roles/logging.admin
gcloud projects add-iam-policy-binding project-name-314159 --member serviceAccount:terraform-gke@project-name-314159.iam.gserviceaccount.com --role roles/pubsub.admin
gcloud projects add-iam-policy-binding project-name-314159 --member serviceAccount:terraform-gke@project-name-314159.iam.gserviceaccount.com --role roles/cloudscheduler.admin
gcloud projects add-iam-policy-binding project-name-314159 --member serviceAccount:terraform-gke@project-name-314159.iam.gserviceaccount.com --role roles/appengine.appAdmin
```

Finally, create and download into the current directory a key file that Terraform will use to authenticate as the service account against the Google Cloud Platform API:

```shell
gcloud iam service-accounts keys create terraform-gke-keyfile.json --iam-account=terraform-gke@project-name-314159.iam.gserviceaccount.com
```

Terraform configuration is stored in [terraform/](terraform/) directory. 
To work with it, cd and copy `terraform-gke-keyfile.json` inside.

Also, it is recommended to create a dedicated GCS bucket named `fastapi-terraform-gke-example-tf-gke` for that configuration:

```shell
gsutil mb -p project-name-314159 -c regional -l us-east1 gs://fastapi-terraform-gke-example-tf-gke/
```

activate versioning:

```shell
gsutil versioning set on gs://fastapi-terraform-gke-example-tf-gke/
```

and grant read-write permissions to service account:

```shell
gsutil iam ch serviceAccount:terraform-gke@project-name-314159.iam.gserviceaccount.com:legacyBucketWriter gs://fastapi-terraform-gke-example-tf-gke/
```

Create AppEngine app to use CloudScheduler (creation with terraform requires "Owner" role that I'd like to avoid):

```shell
gcloud app create --region=us-east1
```

Configure GKE cluster appropriately, variable values to be set in [variables.auto.tfvars](terraform/variables.auto.tfvars) ([template file](terraform/variables.auto.tfvars.tpl)).

Then run 
```shell
cd terraform
terraform init
terraform plan
```

and if everything in the plan looks ok

```shell
terraform apply
```

Note: there could be errors with CloudSQL user creation - they were fixed by re-running `terraform apply`.

To destroy any created resources, run

```shell
terraform destroy
```

When removing any resources manually, terraform could get unsync and manual state cleanup might be useful:

```shell
terraform state rm "%resource name%"
```

When Terraform is done, we can check the status of the cluster and configure the kubectl command line tool to connect to it with:

```shell
gcloud container clusters list
gcloud container clusters get-credentials gke-cluster --region=us-east1
```

### Setting up deployment with Helm

The resources described in this file allow the tiller pod to create resources in the cluster, apply it with:
```shell
kubectl apply -f tiller.yaml
```

`kubectl` has already set up configuration, so it can create service account for tiller.

```shell
cd %project%
docker build -f docker/backend.dockerfile -t gcr.io/project-name-314159/fastapi-terraform-gke-example .
```

To push the image, one need to add GCR to docker config (for Linux-based images):

```shell
gcloud auth configure-docker
```

Then push created image:

```shell
docker push gcr.io/project-name-314159/fastapi-terraform-gke-example
```

Fill in project [settings](kubernetes/values.yaml) and [secrets](kubernetes/secrets.txt) ([template](kubernetes/secrets.txt.tpl)).
Deploy project secrets:

```shell
kubectl create secret generic fastapi-terraform-gke-example --from-env-file=secrets.txt
```

Then deploy the chart:
```shell
cd kubernetes
helm install fastapi-terraform-gke-example ./
```

IP address of the ingress (may take some time to apply):
```shell
kubectl get ingresses
```

Reserved IP address: 
```shell
gcloud compute addresses describe global-cluster-ip --global
```

To uninstall the chart, run:
```shell
helm delete fastapi-terraform-gke-example
```

For debugging:

```shell
kubectl get pods
kubectl logs %pod-name% -c %container-name%
kubectl describe pod %pod-name%
```

### Setting up CI/CD

Configure the repository for Cloud Build pipeline according to documentation, then set a trigger for CI/CD pipeline.

#### Continuous Integration

Configuration is set in [cloudbuild-ci.yaml](cloudbuild-ci.yaml).

Go to [the trigger page](https://console.cloud.google.com/cloud-build/triggers), and follow [official documentation](https://cloud.google.com/build/docs/automating-builds/create-manage-triggers). 

Create trigger with the following settings:

* Name: fastapi-terraform-gke-example-ci
* Event: Pull request
* Configuration: Cloud Build configuration file
* Cloud Build configuration file location: /cloudbuild-ci.yaml

Trigger (linting and running tests) will work on every Pull Request.


#### Continuous Deployment

Build and push custom helm image:

```shell
cd %somewhere%
git clone https://github.com/GoogleCloudPlatform/cloud-builders-community.git
cd cloud-builders-community/helm
docker build -t gcr.io/project-name-314159/helm .
docker push gcr.io/project-name-314159/helm
```

Set in [cloudbuild.yaml](cloudbuild.yaml) appropriate values:

```yaml
  _CUSTOM_REGION: us-east1
  _CUSTOM_CLUSTER: gke-cluster
```

Go to [the trigger page](https://console.cloud.google.com/cloud-build/triggers), and follow [official documentation](https://cloud.google.com/build/docs/automating-builds/create-manage-triggers). 

Create trigger with the following settings:

* Name: fastapi-terraform-gke-example-deploy-helm
* Event: Push new tag
* Tag (regex): v.*
* Configuration: Cloud Build configuration file
* Cloud Build configuration file location: /cloudbuild.yaml

Open Cloud Build -> Settings -> [Service Account permissions](https://console.cloud.google.com/cloud-build/settings/service-account)
 and for project service account enable "Kubernetes Engine Developer".

Trigger (new container building and deployment) will work on every new tag assignment, just do:

```shell
$ git tag v.x.y.z
$ git push origin main --tags
```

## Troubleshooting

Local application logs are being written to `application.log` (rotated).

Cloud logs can be seen in dashboard by filters:

```
resource.type="k8s_container"
resource.labels.project_id="project-name-314159"
resource.labels.cluster_name="gke-cluster"
resource.labels.container_name=~"fastapi-terraform-gke-example*"
```
