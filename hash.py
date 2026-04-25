from werkzeug.security import generate_password_hash

print(generate_password_hash("dacchuR1519", method="pbkdf2:sha256"))