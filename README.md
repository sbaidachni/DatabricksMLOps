# Introduction

In this repo you can find a template for MLOps (Machine Learning Development and Operations) in Databricks. The template is based on mlflow projects and it's more about how to setup and maintain a development environment rather than about DataOps or deployment into production.

# Repo structure

The primary document that explains MLOps process in details you can find in this [document](docs/mlops_architecture.md).

There are following folders in the repo:

- .azure-pipelines: Azure DevOps pipelines
- docs: related documentation
- projects: MLFlow projects to support by this MLOps process
- libs: a source folder for all libraries in the project to be deployed as wheel files
- databricks-sync: couple utility scripts to deploy local branch code into interactive cluster and sync it back
- mlflow_hooks: an example how to trigger of MLFlow projects in git from a databricks notebook
- mlflow_triggers: shows how to trigger projects from a local computer or DevOps
- notebooks: a sandbox folder

# Key Technologies

- [Azure DataBricks](https://azure.microsoft.com/en-us/services/databricks/)
- [Azure DevOps](https://azure.microsoft.com/en-us/services/devops/)
- [MLFlow](https://mlflow.org/)
