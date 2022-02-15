# Databricks notebook source
# dbutils.library.installPyPI("mlflow")
# dbutils.library.restartPython()

# COMMAND ----------

import mlflow
mlflow.set_experiment("/Shared/scoring_experiment")
mlflow.run(
    "https://<git url>/mlops-poc/_git/mlops-poc#project/ExampleScoringProject",
    backend="databricks",
    backend_config=
    {
      "spark_version": "7.0.x-scala2.12",
      "num_workers": 1,
      "node_type_id": "Standard_DS3_v2"
    })
