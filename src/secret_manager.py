import json
import logging
import os
from functools import wraps
from typing import Dict

import boto3
from botocore.client import BaseClient

class CacheSecrets:
    _secrets = {}

def cache_secret(func):
    @wraps(func)
    def wrapper(self, secret_name_env_var_key, extra_arg_key=None, env_var_name_inject=None, default=None):
        cache_key = (secret_name_env_var_key, extra_arg_key)
        if cache_key in CacheSecrets._secrets:
            return CacheSecrets._secrets[cache_key]

        # Call the original function and store in cache
        secret = func(self, secret_name_env_var_key, extra_arg_key, env_var_name_inject, default)
        CacheSecrets._secrets[cache_key] = secret
        return secret

    return wrapper

class SecretManagerCaller:
    _session: BaseClient = None

    @cache_secret
    def __call__(self, secret_name_env_var_key, extra_arg_key=None, env_var_name_inject=None, default=None):
        logging.info(f"Getting secret", extra={"secret_name_env_var_key": secret_name_env_var_key})
        secret_name = os.environ.get(secret_name_env_var_key, None)
        if not secret_name:
            raise ValueError(f"Environment var of secret name key not found in environment variable: {secret_name_env_var_key}")
        if os.environ.get('ENV', None) == 'DEV':
            return secret_name
        secret = self.get_secret(secret_name)
        if extra_arg_key:
            secret = secret[extra_arg_key]
        if env_var_name_inject:
            os.environ[env_var_name_inject] = secret
        return secret

    @classmethod
    def initialize_secret_manager(cls):
        session = boto3.Session()
        cls._session = session.client('secretsmanager', region_name=os.environ.get("AWS_REGION", "us-east-1"))

    @classmethod
    def session(cls)-> BaseClient:
        if cls._session is None:
            cls.initialize_secret_manager()
        return cls._session

    @classmethod
    def get_secret(cls, name: str) -> Dict:
        secret = json.loads(cls.session().get_secret_value(SecretId=name)['SecretString'])
        return secret

SecretManager = SecretManagerCaller()
# usage:
# SecretManagerCaller.__call__
# class NezilutSettings(BaseSettings):
#
#     AZURE_OPENAI_KEY: str = SecretManager("my secret name var key name", "env var name..", 'api-key')


