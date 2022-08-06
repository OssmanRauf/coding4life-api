from passlib.context import CryptContext
from fastapi_mail import ConnectionConfig

# setting hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Hash the password
def hash(password: str):
    return pwd_context.hash(password)


# Verify if password entered and the hashed are te same
def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# def send_email(user):
    #

# configurations of email confirmation sendig
conf = ConnectionConfig(
    MAIL_USERNAME="coding4lifeblog",
    MAIL_PASSWORD="chuzlkwokuxbpsvf",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_TLS=True,
    MAIL_SSL=False,
    MAIL_FROM="coding4lifeblog@gmail.com",
    TEMPLATE_FOLDER="./core/templates"
)
