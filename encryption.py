import pandas as pd
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher_suite = Fernet(key)

with open("secret.key", "wb") as key_file:
    key_file.write(key)

df = pd.read_csv("data-main.csv")

encrypted_data = df.applymap(lambda x: cipher_suite.encrypt(str(x).encode()).decode())

encrypted_data.to_csv("data-encrypted.csv", index=False)

print("Encryption completed successfully.")
