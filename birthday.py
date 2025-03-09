import os
import pytz
import dotenv
import datetime
import pandas as pd
from cryptography.fernet import Fernet

dotenv.load_dotenv()
key = os.getenv('KEY')

cipher_suite = Fernet(key)

encrypted_df = pd.read_csv("data-encrypted.csv")

df = encrypted_df.apply(lambda col: col.map(lambda x: cipher_suite.decrypt(x.encode()).decode()))

def get_dataframe() -> pd.DataFrame:

    df['Name'] = df['Name'].apply(lambda x : x.title())
    df['Contact No.'] = pd.to_numeric(df['Contact No.'], errors='coerce')
    df['Contact No.'] = df['Contact No.'].apply(lambda x: str(x)[:-2])
    df['Roll No'] = df['Roll No'].astype(str)
    df['Registration No'] = df['Registration No'].astype(str)

    today = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).replace(hour=0, minute=0, second=0, microsecond=0).replace(tzinfo=None)
    # today = today.replace(day=28, month=6) # if we want to change today's date

    birthday_index = []

    for index, dob in enumerate(df.iloc[:,1]):

        birthday = datetime.datetime.strptime(dob, '%Y-%m-%d %H:%M:%S')
        birthday = birthday.replace(year=datetime.datetime.now().year)

        if today == birthday:
            birthday_index.append(index)

    if not birthday_index: return pd.DataFrame()

    birthday_df = df.loc[birthday_index, :]
    birthday_df['Age'] = birthday_df['DOB'].apply(lambda dob : datetime.datetime.now().year - datetime.datetime.strptime(dob, '%Y-%m-%d %H:%M:%S').year)
    birthday_df = birthday_df[['Name', 'DOB', 'Age', 'Section', 'Contact No.', 'Roll No', 'Registration No', 'Gender', 'Hosteller Or Day Scholar', 'Email ID']]
    birthday_df['DOB'] = birthday_df['DOB'].apply(lambda x : '-'.join(x[:10].split('-')[::-1]))

    birthday_df = birthday_df.reset_index().drop('index', axis=1)

    return birthday_df
