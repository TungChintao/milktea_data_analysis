import pandas as pd
from sqlalchemy import create_engine


keyword = pd.read_csv('keywords.csv')
engine = create_engine('mysql+pymysql://user:password@host:3306/milktea')


def csv_to_sql():
    keyword.to_sql('wordcloud', engine, index=False, if_exists='append')


if __name__ == "__main__":
    csv_to_sql()
