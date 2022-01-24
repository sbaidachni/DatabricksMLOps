import os
import subprocess
from dotenv import load_dotenv
from databricks_cli.sdk import ApiClient
from databricks_cli.sdk.service import WorkspaceService
from requests.exceptions import HTTPError
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
  
    db = ApiClient(
        host=f"{domain}",
        token=token
    )

    db_wrksp = WorkspaceService(db)

    try:
        print("Checking if the folder exists")
        db_wrksp.get_status(remote_folder)
    except HTTPError as err:
        if "RESOURCE_DOES_NOT_EXIST" in str(err.response.content):
            print("The databricks folder doesn't exist")
            exit(-1)
        else:
            raise err

    DownloadFiles(db_wrksp, os.path.join(project_folder, notebook_folder), remote_folder)

def DownloadFiles(db_wrksp, local_folder, remote_folder):
    print(f"Checking {remote_folder}")
    os.makedirs(local_folder, exist_ok=True)
    f_objs = db_wrksp.list(remote_folder)
    if 'objects' in f_objs:
        for f_obj in f_objs['objects']:
            if f_obj['object_type']=='NOTEBOOK':
                file_name = f_obj['path'].split('/')[-1]
                if f_obj['language']=='PYTHON':
                    file_name = file_name + '.py'
                elif f_obj['language']=='SCALA':
                    file_name = file_name + '.scala'
                elif f_obj['language']=='SQL':
                    file_name = file_name + '.sql'
                elif f_obj['language']=='R':
                    file_name = file_name + '.r'
                else:
                    # if they add more types...
                    continue
                print(f"Copying {f_obj['path']} to {file_name}")
                content = db_wrksp.export_workspace(f_obj['path'], format="SOURCE")
                with open(os.path.join(local_folder, file_name), "w+") as f:
                    decodedBytes = base64.b64decode(content['content'])
                    decodedStr = str(decodedBytes, "utf-8")
                    f.write(decodedStr)
            elif f_obj['object_type']=='DIRECTORY':
                new_local_folder = os.path.join(
                    local_folder,
                    f_obj['path'].split('/')[-1])
                DownloadFiles(db_wrksp, new_local_folder, f"{f_obj['path']}")

if __name__ == "__main__":
    main()
