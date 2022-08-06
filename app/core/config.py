from pydantic import BaseSettings


# Settings class takes the environment variables and puts it into an object
class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_name: str
    database_password: str
    database_username: str
    secreat_key: str
    algorithm: str
    access_token_expiration_time: int
    refresh_token_expiration_time: int
    mail_password: str
    mail_adress: str

    class Config:
        env_file = ".env"


settings = Settings()
