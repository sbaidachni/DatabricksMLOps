import os
import subprocess
from dotenv import load_dotenv
from databricks_cli.sdk import ApiClient
from databricks_cli.sdk.service import WorkspaceService
from requests.exceptions import HTTPError
from argparse import ArgumentParser
import base64

def main():
    load_dotenv()

    domain = os.environ.get("DATABRICKS_HOST")
    token = os.environ.get("DATABRICKS_TOKEN")
    notebook_folder = os.environ.get("NOTEBOOK_FOLDER")
    project_folder = os.environ.get("PROJECT_FOLDER")
    user = os.environ.get("USER")

    git_branch = subprocess.check_output(
        "git rev-parse --abbrev-ref HEAD",
        shell=True,
        universal_newlines=True).strip()
    remote_folder = f"/Users/{user}/{git_branch}/{notebook_folder}"

    parser = ArgumentParser()

    parser.add_argument(
        '--overwrite',
        dest='overwrite',
        action='store_true')

    args = parser.parse_args()

    db = ApiClient(
        host=f"{domain}",
        token=token
    )

    db_wrksp = WorkspaceService(db)

    is_avaliable = True

    try:
        print("Checking if the folder exists")
        db_wrksp.get_status(remote_folder)
    except HTTPError as err:
        # potentially we can check 404 as a status code, but RESOURCE_DOES_NOT_EXIST
        # is in the documentation
        if "RESOURCE_DOES_NOT_EXIST" in str(err.response.content):
            is_avaliable = False
        else:
            raise err

    if is_avaliable is True:
        if args.overwrite:
            print(f"Deleting the existing folder {remote_folder}")
            db_wrksp.delete(remote_folder, recursive=True)
        else:
            print("The folder already exists.")
            print("If you really would like to overwrite the folder, add --overwite parameter")
            exit(-1)

    MoveFiles(db_wrksp, os.path.join(project_folder, notebook_folder), remote_folder)

def MoveFiles(db_wrksp, local_folder, remote_folder):
    print(f"Creating {remote_folder}")
    db_wrksp.mkdirs(remote_folder)
    f_objs = os.listdir(local_folder)
    for f_obj in f_objs:
        full_path = os.path.join(local_folder, f_obj)
        if os.path.isdir(full_path):
            MoveFiles(db_wrksp, full_path, f"{remote_folder}/{f_obj}")
        else:
            if full_path.endswith(".py"):
                language='PYTHON'
                n_name = f_obj.replace('.py','')
            elif full_path.endswith(".scala"):
                language='SCALA'
                n_name = f_obj.replace('.scala','')
            elif full_path.endswith(".sql"):
                language='SQL'
                n_name = f_obj.replace('.sql','')
            elif full_path.endswith(".r"):
                language='R'
                n_name = f_obj.replace('.r','')
            else:
                print(f"Skipping {f_obj}")
                continue
            
            print(f"Moving {full_path}")
            with open(full_path) as f:
                block = f.read()
                encodedBytes = base64.b64encode(block.encode("utf-8"))
                encodedStr = str(encodedBytes, "utf-8")
            db_wrksp.import_workspace(
                    f"{remote_folder}/{n_name}", format="SOURCE", language=language, content=encodedStr)
                

if __name__ == "__main__":
    main()
