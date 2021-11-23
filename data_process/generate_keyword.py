import os
import jieba
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

shops = pd.read_csv(f'../milktea_shop.csv')
# shops = shops.loc[shops.isMain].drop(['isMain', 'backCateName'], axis=1)
goods = pd.read_csv(f'../milktea_good.csv')
# goods = goods.loc[goods.shopid.isin(shops.shopid)]
drop_list = ['中杯', '叠加', '使用', '饮品', '兄弟', '招牌', '份', '书亦烧', '系列', '建议',
            '单人', '套餐', '满杯', '双人', '大叔', '小姐姐', '网红', '快乐', '经典', '不知',
             '特饮', '人气', '热饮', '特色', '必点', '双重', '热销', '全场', '通用', '代金券',
             '张', '元', '使用', '兑换券', '餐', '汉堡', 'A', 'W', '适用', '仅', '堡', '鸡腿',
             '热', '冰', 'WIFI','爆款', 'W34', '咖啡', 'L', '下午茶', '可', '只', '选', '提供',
             '香辣', '大杯', '1000cc', '小料', 'WOW', '中', '阴阳师', '肯德基']

text = ' '.join(goods.good)
jieba.load_userdict(os.path.join(os.path.abspath(''), 'keyword.txt'))
words = pd.Series(jieba.cut(text, cut_all=False))
stopwords = set(words.value_counts().head(13).index)
print(stopwords)
for w in drop_list:
    stopwords.add(w)


wc = WordCloud(
    width=1920, height=1080, background_color='#1a1a1a',
    font_path='STXINWEI.TTF',
    stopwords=stopwords, max_font_size=400,
    random_state=50)

wc.generate_from_text(' '.join(words))
# wc.to_file('try.png')
keywords = []
level = ' '.join(list(wc.words_.keys())).split(' ')

for w in words:
    if w in level:
        keywords.append(w)

pd.DataFrame({'keyword': keywords}).to_csv('keywords2.csv')





