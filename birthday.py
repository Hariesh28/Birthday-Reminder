import os
import pytz
import dotenv
import pandas as pd
from cryptography.fernet import Fernet
from functools import lru_cache

# Load your Fernet key
dotenv.load_dotenv()
KEY = os.getenv('KEY')
cipher = Fernet(KEY)


@lru_cache(maxsize=1)
def _load_decrypted_df() -> pd.DataFrame:
    """
    Read the encrypted CSV once, decrypt every cell, parse DOB column,
    and cache the result for future calls.
    """
    enc = pd.read_csv("data-encrypted.csv")
    df = enc.apply(lambda col: col.map(lambda x: cipher.decrypt(x.encode()).decode()))

    df['DOB'] = pd.to_datetime(df['DOB'], format='%Y-%m-%d %H:%M:%S')
    return df


def get_dataframe() -> pd.DataFrame:
    """
    Return a DataFrame of people whose birthday is today.
    """
    df = _load_decrypted_df().copy()

    df['Name']            = df['Name'].str.title()
    df['Contact No.']     = df['Contact No.'].str[:-2]
    df['Roll No']         = df['Roll No'].astype(str)
    df['Registration No'] = df['Registration No'].astype(str)

    today = pd.Timestamp.now(pytz.timezone('Asia/Kolkata')).normalize().tz_localize(None)
    # today = today.replace(day=28, month=6) # if we want to change today's date

    mask = (df['DOB'].dt.month == today.month) & (df['DOB'].dt.day == today.day)
    today_df = df.loc[mask].copy()

    if today_df.empty:
        return pd.DataFrame()

    # Compute age and reformat DOB
    today_df['Age'] = today.year - today_df['DOB'].dt.year
    today_df['DOB'] = today_df['DOB'].dt.strftime('%d-%m-%Y')

    cols = [
        'Name','DOB','Age','Section','Contact No.','Roll No',
        'Registration No','Gender','Hosteller Or Day Scholar','Email ID'
    ]
    return today_df[cols].reset_index(drop=True)


def get_upcoming_birthdays(n: int = 2) -> pd.DataFrame:
    """
    Return a DataFrame of the next `n` distinct future days (1–365)
    that have birthdays, listing all birthdays on each such day.
    """
    df = _load_decrypted_df().copy()

    today = pd.Timestamp.now(pytz.timezone('Asia/Kolkata')).normalize().tz_localize(None)

    df['this_bday'] = df['DOB'].apply(lambda dt: dt.replace(year=today.year))

    passed = df['this_bday'] < today
    df.loc[passed, 'this_bday'] = df.loc[passed, 'this_bday'] + pd.DateOffset(years=1)

    df['delta'] = (df['this_bday'] - today).dt.days

    up = df[df['delta'] > 0].sort_values('delta')

    upcoming_deltas = up['delta'].unique()[:n]
    sel = up[up['delta'].isin(upcoming_deltas)].copy()

    # Format for display
    sel['Birthday Date'] = sel['this_bday'].dt.strftime('%d-%m-%Y')
    sel['Age on Day']    = sel['this_bday'].dt.year - sel['DOB'].dt.year
    sel['DOB']           = sel['DOB'].dt.strftime('%d-%m-%Y')

    return sel[[
        'Birthday Date','Name','DOB','Age on Day','Section','Email ID'
    ]].reset_index(drop=True)


def get_missed_birthdays() -> pd.DataFrame:
    """
    Return a DataFrame of people whose birthday was exactly yesterday.
    """
    df = _load_decrypted_df().copy()

    today     = pd.Timestamp.now(pytz.timezone('Asia/Kolkata')).normalize().tz_localize(None)
    yesterday = today - pd.Timedelta(days=1)

    mask = (df['DOB'].dt.month == yesterday.month) & (df['DOB'].dt.day == yesterday.day)
    miss = df.loc[mask].copy()

    if miss.empty:
        return pd.DataFrame()

    miss['Missed Date']   = yesterday.strftime('%d-%m-%Y')
    miss['Age on Missed'] = yesterday.year - miss['DOB'].dt.year
    miss['DOB']           = miss['DOB'].dt.strftime('%d-%m-%Y')

    return miss[[
        'Missed Date','Name','DOB','Age on Missed','Section','Email ID'
    ]].reset_index(drop=True)
