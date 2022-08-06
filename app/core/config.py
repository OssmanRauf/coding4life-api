from pydantic import BaseSettings


# Settings class takes the environment variables and puts it into an object
class Settings(BaseSettings):
    database_url: str
    secreat_key: str
    algorithm: str
    access_token_expiration_time: int
    refresh_token_expiration_time: int
    mail_password: str
    mail_adress: str

    class Config:
        env_file = ".env"


settings = Settings()
