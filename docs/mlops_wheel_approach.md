# Using Python Wheel for custom Python packages

If your code repository requires a custom python package (i.e. [libs/mylib](../libs/mylib/)) that is to be used in some notebook based coding environment like Databricks, it might be ideal to create a Python wheel. A Python wheel is a method of importing your modules by installing it in the Databricks cluster using a `.whl` file.

To begin, keep your Python modules and packages in the root directory, `lib`. Inside the `lib` directory, you can create a package directory for your custom library (i.e. `mylib`). Each package directory should have an `__init__.py` in addition to other python files to make the package run.

In this approach, we have provided a workflow using Azure DevOps Build pipelines to automate the creation and installation of a wheel file. To do this, import [`mlops_install_wheel_master.yml`](.azure_pipeline/mlops_install_wheel_master.yml) as a Build pipeline. The Build pipeline will 1) create all wheel files (i.e. `.whl`) for all custom Python libraries 2) copy all `.whl` files over to the Databricks cluster DBFS and 3) install them on the cluster.

In the root of the `lib` directory, there are two scripts that are called by Build pipelines: (1) `deploy_wheel.py` and (2) `setup.py`. The `setup.py`, which includes the distribution name, version number, and list of package name, is used in the `mlops_install_wheel_master` pipeline to create the `.whl` file. Next, the `deploy_wheel.py` is used in the `mlops_run_pipelines_pr` pipeline to ensure that the custom Python packages are deployed in the Databricks cluster environment before executing the training or scoring scripts that depend on the custom Python packages. In order to ensure that your training and scoring scripts are indeed relying on the custom packages, you will need to modify the `env.yaml` (i.e. [training_env.yaml](../projects/ExampleTrainingProject/training_env.yaml)) in the project directory to specify the custom packages as dependencies in the environment. For example,

```yaml
name: training
channels:
  - defaults
  - anaconda
  - conda-forge
dependencies:
  - python=3.7
  - scikit-learn
  - pip:
    - mlflow
    - /dbfs/libs/mylib-1.0-py3-none-any.whl
```
