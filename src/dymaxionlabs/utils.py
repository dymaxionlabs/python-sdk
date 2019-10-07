import os


def get_api_url():
    """Get current API URL from environment"""
    return os.getenv("DYM_API_URL", "https://api.dymaxionlabs.com")


def get_api_key():
    """Get current API Key from environment"""
    return os.environ.get("DYM_API_KEY")


def get_project_id():
    """Get current Project uuid from environment"""
    return os.environ.get("DYM_PROJECT_ID")
