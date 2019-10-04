import os


def get_api_url():
    return os.getenv("DYM_API_URL", "https://api.dymaxionlabs.com")


def get_api_key():
    return os.environ.get("DYM_API_KEY")


def get_project_id():
    return os.environ.get("DYM_PROJECT_ID")
