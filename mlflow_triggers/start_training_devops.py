import mlflow
from dotenv import load_dotenv
from databricks_cli.sdk import ApiClient
from databricks_cli.sdk.service import WorkspaceService
from requests.exceptions import HTTPError
import subprocess
import os

def main():
    load_dotenv()
    domain = os.environ.get("DATABRICKS_HOST")
    token = os.environ.get("DATABRICKS_TOKEN")
    root_exp_dir = os.environ.get("ROOT_EXP_DIR")
    user = os.environ.get("USER")
    git_branch = os.environ.get("BUILD_SOURCEBRANCHNAME")
    user = user.replace(" ","")
    model_name = os.environ.get("MODEL_NAME")

    if git_branch is None:
        git_branch = subprocess.check_output(
            "git rev-parse --abbrev-ref HEAD",
            shell=True,
            universal_newlines=True).strip()

    if model_name is None:
        model_name = f"{git_branch}_model"

    root_folder = f"/{root_exp_dir}/{user}"
    experiment_folder = f"/{root_exp_dir}/{user}/{git_branch}_expr"
    print(f"Experiment folder: {experiment_folder}")

    db = ApiClient(
        host=f"{domain}",
        token=token
    )

    db_wrksp = WorkspaceService(db)

    try:
        print("Checking if the folder exists")
        db_wrksp.get_status(root_folder)
    except HTTPError as err:
        if "RESOURCE_DOES_NOT_EXIST" in str(err.response.content):
            db_wrksp.mkdirs(root_folder)
        else:
            raise err

    mlflow.set_experiment(experiment_folder)
    mlflow.run(
        "projects/ExampleTrainingProject",
        backend="databricks",
        backend_config="projects/ExampleTrainingProject/cluster.json",
        parameters={"model_name":model_name})

if __name__ == "__main__":
    main()
