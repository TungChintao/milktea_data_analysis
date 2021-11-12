import pymysql
import requests
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
import threading

db = pymysql.connect(host='localhost', user='user', password='password', port=3306, db='schema')
engine = create_engine('mysql+pymysql://user:password@localhost:3306/schema')

S = '•'


def locationToAddress(location):
    parameters = {
                    'location': location,
                    'key': "......."
                 }
    base = 'https://restapi.amap.com/v3/geocode/regeo?'
    response = requests.get(base, params=parameters)
    answer = response.json() #.encode('gbk','replace')
    # print(answer)
    return answer['regeocode']['addressComponent']['district']


def table_insert(id, value):
    cursor = db.cursor()
    sql3 = 'UPDATE clean_shop_data2 SET address=%s WHERE shopid=%s'
    try:
        cursor.execute(sql3, (value, id))
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()


def close_connect():
    db.close()


def tidy_shops():
    sql = '''   
            select * from clean_shop_data2;
          '''
    df = pd.read_sql(sql, engine)
    num = 1
    df['title'] = df.title.map(lambda s: s.split('（')[0])
    df['title'] = df.title.str.replace(S, '·')
    df['isMain'] = df.backCateName.map(lambda cat: True if ('奶茶' in cat or '冰淇淋' in cat or '甜品' in cat) else False)
    for i, r in df.iterrows():
        shopid = r['shopid']
        adr = str(str(r['longitude']) + ',' + str(r['latitude']))
        a = locationToAddress(adr)
        print(num, a)
        num+=1
        table_insert(shopid, a)
    close_connect()


def tidy_goods():
    sql = '''   
               select * from milktea_good;
             '''
    df = pd.read_sql(sql, engine)
    df.to_sql('clean_good_data', engine, index=False,
              dtype={
                  'shopid': sqlalchemy.types.VARCHAR(20),
                  'title': sqlalchemy.types.VARCHAR(200),
              })
    with engine.connect() as con:
        con.execute('ALTER TABLE clean_good_data ADD PRIMARY KEY (`shopid`, `title`)')
        con.execute('ALTER TABLE clean_good_data ADD FOREIGN KEY shopid(shopid) references clean_shop_data2(shopid)')


def unify_values(df, col, to_value, *alters):
    for alt in alters:
        df[col] = df[col].str.replace(alt, to_value)
    return df


def processing_shops():
    sql = '''   
            select * from clean_shop_data2;
          '''
    shops = pd.read_sql(sql, engine)
    # print(shops)
    shops = shops.drop_duplicates().reset_index().drop(['index'], axis=1)
    shops = shops.loc[shops.isMain == 1].drop(['isMain', 'backCateName'], axis=1)
    unique_top_list = list(shops.title.value_counts().head(100).index)
    unique_top_list.sort()
    replace_dict = {
        '1 点点': ['1點點', '一點點', '1点点', '1 點點', '1 點點 ', '1 點點奶茶'],
        '700CC': ['700CC天然苏打水茶饮', '700cc都市茶饮'],
        'CoCo都可': ['coco都可'],
        'HEY JUICE 茶桔便': ['HEY JUICE茶桔便', 'HEYJUICE茶桔便'],
        '皇茶': ['royaltea皇茶'],
        '丸摩堂': ['丸摩堂100%鲜果茶'],
        '厝内小眷村': ['厝内小眷村cuo nei village'],
        '嘿糖': ['嘿糖鲜奶茶饮'],
        '大卡司': ['大卡司DAKASI'],
        '快乐柠檬': ['快乐柠檬happy lemon', '快乐柠檬happylemon', 'happy lemon快乐柠檬'],
        '蜜雪冰城': ['蜜雪冰城·冰淇淋与茶'],
        '贡茶': ['贡茶GONGCHA']
    }
    for k, v in replace_dict.items():
        shops = unify_values(shops, 'title', k, *v)

    shops = shops.loc[shops.avgprice > 0]
    shops = shops.loc[shops.comments >= 0]
    print(shops.avgprice)


def thread_request():
    for i in range(20):
        t = threading.Thread(target=tidy_shops, name="thread-" + str(i))
        t.start()
        t.join()


if __name__ == '__main__':
    tidy_shops()
    thread_request()
    tidy_goods()
    processing_shops()