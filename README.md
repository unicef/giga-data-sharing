# Giga Data Sharing

## Prerequisites

- [ ] [Docker](https://docker.com)
- [ ] [Task](https://taskfile.dev)

## Local Development

1. Copy the file `.env.example` into a new file named `.env`.
2. Fill in the required values in `.env` or get them from Bitwarden.
    - For values prefixed with `$`, this means you can run the specified command to
      generate the value yourself
3. Run `task` to launch the containers.
4. Run the following to create the database tables and seed the initial roles and admin
   token:
    ```shell
    task migrate
    task load-fixtures -- roles api_keys
    ```
5. To [interact](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md) with
   the Delta Sharing server you can:
    1. Access the Swagger UI at https://localhost:5000 and use the built-in
       **Try it out** examples.
    2. Use an API testing tool like Postman or Insomnia to send requests to the server.
6. To get the initial bearer token, refer to the `.env` you created earlier and
   look for the keys `ADMIN_API_KEY` and `ADMIN_API_SECRET`. The admin bearer token is
   constructed as
   ```text
   ADMIN_API_KEY:ADMIN_API_SECRET
   ```

## Deployment

Deployments are performed automatically through Azure DevOps when pushing/merging to
certain branches. The branch-environment mapping is as follows:

| Branch       | Environment                                  |
|--------------|----------------------------------------------|
| `main`       | [DEV](https://io-datasharing-dev.unitst.org) |
| `staging`    | [STG](https://io-datasharing-stg.unitst.org) |
| `production` | PRD (WIP)                                    |

To get the initial bearer token, you can either:

- Inspect the Azure DevOps pipeline variables and look for the `ADMIN_API_KEY` and
  `ADMIN_API_SECRET` values. Concatenate them in the same manner as described in
  the [Local Development](#local-development) section.
- If you have CLI access to the K8s cluster, run
   ```shell
   kubectl get secrets giga-data-sharing -o yaml | yq .data
   ```
  Ensure you have the [yq](https://github.com/mikefarah/yq) tool installed.
