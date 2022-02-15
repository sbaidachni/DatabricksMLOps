import os
import subprocess
from dotenv import load_dotenv
from databricks_cli.sdk import ApiClient
from databricks_cli.sdk.service import DbfsService
from requests.exceptions import HTTPError
import base64

def main():
    load_dotenv()
    domain = os.environ.get("DATABRICKS_HOST")
    token = os.environ.get("DATABRICKS_TOKEN")
    user = os.environ.get("USER")
    project_folder = os.environ.get("PROJECT_FOLDER")
    git_branch = os.environ.get("BUILD_SOURCEBRANCHNAME")

    if git_branch is None:
        git_branch = subprocess.check_output(
            "git rev-parse --abbrev-ref HEAD",
            shell=True,
            universal_newlines=True).strip()

    db = ApiClient(
        host=f"{domain}",
        token=token
    )

    print('Getting access to dbfs service')
    dbfs = DbfsService(db)

    # In fact, we need to use a dynamic path here,
    # but we will need to generate training_env.yaml
    # dynamically in this case
    dbfs_path = f"/libs/" #{user}/{git_branch}"
    print(f'Deleting {dbfs_path}')
    dbfs.delete(dbfs_path, recursive=True)

    print(f'Moving libraries to dbfs')

    for dirs in os.listdir(os.path.join(project_folder, 'libs')):
        if os.path.isdir(os.path.join(project_folder, 'libs', dirs)):
            MoveFiles(dbfs, os.path.join(project_folder, 'libs', str(dirs), 'dist'), dbfs_path)

def MoveFiles(dbfs, local_folder, remote_folder):
    print(f"Creating {remote_folder}")
    dbfs.mkdirs(remote_folder)
    f_objs = os.listdir(local_folder)
    for f_obj in f_objs:
        full_path = os.path.join(local_folder, f_obj)
        if os.path.isdir(full_path):
            MoveFiles(dbfs, full_path, f"{remote_folder}/{f_obj}")
        else:
            if not full_path.endswith(".whl"):
                print(f"Skipping {f_obj}")
                continue

            print(f"Moving {full_path}")
            with open(full_path, "rb") as f:
                block = f.read()
                encodedBytes = base64.b64encode(block)
                encodedStr = str(encodedBytes, "utf-8")
            dbfs.put(
                f"{remote_folder}/{f_obj}", contents=encodedStr)


if __name__ == "__main__":
    main()
