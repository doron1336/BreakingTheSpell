from src.secret_manager import SecretManagerCaller

SecretManager = SecretManagerCaller()


class LLMSettings:
    AZURE_OPENAI_KEY: str = SecretManager('OPENAI_API_4O_SECRET_NAME', extra_arg_key='api-key')
    AZURE_OPENAI_ENDPOINT: str = "https://lqc-gpt-4o.openai.azure.com/"
    AZURE_MODEL_IMAGE_DEPLOYMENT_ID: str = "lqc-4o"
    OPENAI_API_VERSION: str = "2024-08-01-preview"
    OPENAI_MODEL: str = "gpt-4o"
    LIQUIDITY_ENDPOINT: str = "https://lqc-server-gateway.liquidity-capital.com/graphql"
    NEZILUT_JS_API_PATH: str = ''
    FETCH_GRAPHQL_EMAIL_ADDRESS: str = ""
    FETCH_GRAPHQL_PASSWORD: str = ""
