import os
import requests


TF_API_URL = os.environ["TF_API_URL"].strip("\n").strip()
TF_API_KEY = os.environ["TF_API_KEY"].strip("\n").strip()
TF_ORGANIZATION = os.environ["TF_ORGANIZATION"].strip("\n").strip()


def get_auto_destroy_workspaces():
    url = f"{TF_API_URL}/organizations/{TF_ORGANIZATION}/workspaces"
    headers = {
        "Authorization": f"Bearer {TF_API_KEY}",
        "Content-Type": "application/vnd.api+json",
    }
    params = {
        "search[tags]": "auto-destroy",
    }

    res = requests.get(url=url, headers=headers, params=params).json()
    workspaces = map(
        lambda x: {"name": x["attributes"]["name"], "id": x["id"]}, res["data"]
    )
    return workspaces


def get_workspace_resouce_count(workspace_id):
    url = f"{TF_API_URL}/workspaces/{workspace_id}/resources"
    headers = {
        "Authorization": f"Bearer {TF_API_KEY}",
        "Content-Type": "application/vnd.api+json",
    }

    res = requests.get(url=url, headers=headers).json()
    return len(res["data"])


def trigger_destroy(workspace_id):
    url = f"{TF_API_URL}/runs"
    headers = {
        "Authorization": f"Bearer {TF_API_KEY}",
        "Content-Type": "application/vnd.api+json",
    }

    payload = {
        "data": {
            "attributes": {
                "is-destroy": True,
                "auto-apply": True,
                "message": "Auto-destroy triggered by tf-cloud-destroy-lambda",
            },
            "relationships": {
                "workspace": {
                    "data": {
                        "id": workspace_id,
                        "type": "workspaces",
                    }
                }
            },
        }
    }

    res = requests.post(url=url, headers=headers, json=payload).json()
    return res["data"]["id"]  # return run id


def handler(event, context):
    # fetch all workspaces with auto-destroy tag
    workspaces = get_auto_destroy_workspaces()

    for workspace in workspaces:
        # check if workspace has resources
        resource_count = get_workspace_resouce_count(workspace["id"])
        print("======================================================")
        print(f"Workspace: {workspace['name']} ({workspace['id']})")
        print("======================================================")
        if resource_count > 0:
            print(f"{resource_count} to destroy...\n")
            # trigger destroy
            run_id = trigger_destroy(workspace["id"])
            print(f"Destroy triggered: {run_id}")

        else:
            print(f"No resources to destroy")


if __name__ == "__main__":
    handler(None, None)
