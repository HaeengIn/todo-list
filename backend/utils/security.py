# Import required modules
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Set password hahser
password_hasher = PasswordHasher()


# Verify password
def VerifyPassword(hashed_password: str, password: str) -> bool:
    try:
        return password_hasher.verify(hashed_password, password)
    except VerifyMismatchError:
        return False
