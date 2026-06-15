import os
from dotenv import load_dotenv

load_dotenv()


def get_setting(key: str, default=None):
    """
    Priority:
    1. .env / environment variable
    2. Streamlit secrets.toml / Streamlit Cloud Secrets
    3. default
    """

    env_value = os.getenv(key)

    if env_value is not None and env_value != "":
        return env_value

    try:
        import streamlit as st

        if key in st.secrets:
            secret_value = st.secrets[key]

            if secret_value is not None and secret_value != "":
                return secret_value

    except Exception:
        pass

    return default


def require_setting(key: str):
    value = get_setting(key)

    if value is None or value == "":
        raise RuntimeError(
            f"Missing required setting: {key}. "
            f"Add it to .env locally or Streamlit Cloud Secrets."
        )

    return value