# Cloud Computing Semester Project
*Matthias Kellner, Nicklas Neu, Johanna Preining*

## Proposal
### Goal of the project
The high-level goal of the project is to implement a successful and well-defined git branching model to enable continuous integration for a simple dummy app. This aims to simplify the process of code management and testing upon merging and releasing. Furthermore, we want to gain knowledge regarding the definition of GitHub Actions and how to incorporate continuous integration into a GitHub project. 

In order to reach these goals, we need a core application to be able to use and test the git workflows. Unfortunately, there is no suitable application, which already exists. Therefore, we need to build a simple application from scratch, which we will use as a base for this project. Then, we will define a git flow strategy together with an appropriate documentation in order to implement it correctly using GitHub Actions.

The core application is a simple file organization tool that enables users to upload and download files to and from a MINIO storage. With a user-friendly Streamlit frontend, it provides seamless access to all essential functionalities.

The cloud computing aspect in this project lies in the usage of the cloud-based service GitHub Actions, the Google Kubernetes Engine and the Google Cloud Registry.

### Milestones
Break down the project into milestones, including team-internal deadlines

1. Writing the proposal -> *17/12/2024*
2. Adding the dummy project -> *26/12/2024*
3. Defining git flow strategy -> *06/01/2025*
4. Implementing git flow strategy using GitHub Actions -> *20/01/2025*
3. Creating the presentation -> *31/02/2025*
4. Presenting the project -> *03/02/2025*

### Distribution of work and responsibilities
1. Writing the proposal: Matthias, Nicklas, Johanna
2. Adding the dummy project: Matthias
3. Define git flow strategy: Johanna
4. Implementing git flow strategy using GitHub Actions: Matthias, Nicklas, Johanna
3. Creating the presentation: Nicklas
4. Presenting the project: Matthias, Nicklas, Johanna

## Implementation
### Git Flow Strategy
In this project, we follow a simple Git flow strategy to maintain a structured and efficient development process.

#### Main Branch (`main`)
The `main` branch contains the production-ready version of the code at all times. The HEAD of this branch always reflects a stable and deployable version of the application. Once a new version is pushed to the `main` branch, the application should be automatically built, containerized, and deployed to the Google Kubernetes Engine (GKE) cluster

#### Development Branch (`develop`)
The `develop` branch is the main working branch for developers. It serves as an integration branch where all feature branches are merged before they are included in `main`.

#### Feature Branches (`feature/*`)
Each new feature is developed on a dedicated feature branch. These branches allow developers to work independently on new functionality without affecting the stability of the `develop` branch. Once a feature is completed and reviewed, it is merged into `develop`.

#### Small Fixes & Refactoring
Small bug fixes, refactoring, and configuration changes can be made directly in the `develop` branch. For larger changes, a separate feature branch should be created.

#### Merging & Releases
1. **Feature branches** are merged into `develop` once they are completed and reviewed.
2. **`develop` is tested and refined** before being merged into `main` for a release.
3. **Releases are tagged** in the `main` branch to mark stable versions of the software.

This workflow ensures a structured, collaborative, and organized development process while keeping the `main` branch stable and production-ready.

### Deployment Process & GitHub Actions Workflow
To deploy the application, the following steps are performed:

#### Deployment Steps
1. **Checkout Commit** – Retrieve the latest code from the `main` branch.
2. **Google Cloud Authentication** – Authenticate with Google Cloud to enable service interactions.
3. **Docker Authentication** – Configure authentication to push images to Google Artifact Registry (GAR).
4. **Build & Push Docker Image** – Create a Docker image and push it to GAR.
5. **Setup Kustomize** – Install and configure Kustomize for Kubernetes manifest management.
6. **Deploy to Google Kubernetes Engine (GKE)** – Apply the updated Kubernetes configuration and ensure a successful rollout.

#### Implementation in GitHub Actions
These deployment steps are automated using a GitHub Actions workflow that runs on every push to the `main` branch. Below is a breakdown of how each step is executed in the provided workflow file:

##### 1. Checkout Commit
- The workflow starts by checking out the latest commit using:
  ```yaml
  - name: 'Checkout'
    uses: 'actions/checkout@v4'
  ```

##### 2. Google Cloud Authentication
- The service account key is used to authenticate with Google Cloud:
  ```yaml
  - name: Authenticate with Google Cloud
    uses: google-github-actions/auth@v2
    with:
      credentials_json: ${{ secrets.GCLOUD_SERVICE_KEY }}
  ```

##### 3. Debug Service Account
- Debugging step to check project ID and configuration:
  ```yaml
  - name: Debug Service Account
    run: |
      echo "Project ID from Key:"
      jq '.project_id' key.json || echo "Could not read project_id"
      gcloud config list
  ```

##### 4. Docker Authentication
- Docker authentication is set up to push images to GAR:
  ```yaml
  - name: Configure Docker Authentication
    run: |
      gcloud auth configure-docker ${{ env.GAR_LOCATION }}-docker.pkg.dev
  ```

##### 5. Set up GKE Credentials
- Retrieve credentials to interact with the GKE cluster:
  ```yaml
  - name: Set up GKE credentials
    uses: google-github-actions/get-gke-credentials@v2
    with:
      cluster_name: ${{ env.GKE_CLUSTER }}
      location: ${{ env.GKE_ZONE }}
  ```

##### 6. Build & Push Docker Image
- A Docker image is built and tagged with `latest`, then pushed to GAR:
  ```yaml
  - name: 'Build and push Docker container'
    run: |-
      DOCKER_TAG="${{ env.GAR_LOCATION }}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE}:latest"

      docker build \
        --tag "${DOCKER_TAG}" \
        --build-arg GITHUB_SHA="${GITHUB_SHA}" \
        --build-arg GITHUB_REF="${GITHUB_REF}" \
        .

      docker push "${DOCKER_TAG}"
  ```

##### 7. Setup Kustomize
- Kustomize is installed and made executable:
  ```yaml
  - name: 'Set up Kustomize'
    run: |-
      curl -sfLo kustomize https://github.com/kubernetes-sigs/kustomize/releases/download/v3.1.0/kustomize_3.1.0_linux_amd64
      chmod u+x ./kustomize
  ```

##### 8. Deploy to Google Kubernetes Engine
- Kustomize is used to update the deployment configuration, and Kubernetes resources are applied:
  ```yaml
  - name: 'Deploy to GKE'
    run: |-
      cd k8s
      ../kustomize edit set image LOCATION-docker.pkg.dev/PROJECT_ID/REPOSITORY/IMAGE:TAG=$GAR_LOCATION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE:latest
      ../kustomize build . | kubectl apply -f - --validate=false
      kubectl rollout status deployment/$DEPLOYMENT_NAME
      kubectl get services -o wide
  ```

This workflow ensures a fully automated deployment process, reducing manual steps and enabling continuous deployment to the Kubernetes cluster.

