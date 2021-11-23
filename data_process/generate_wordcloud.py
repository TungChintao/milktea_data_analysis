import os
import jieba
import jieba.analyse
import pandas as pd
shops = pd.read_csv(f'../milktea_shop.csv')
shops = shops.loc[shops.isMain == 1]
# shops = shops.loc[shops.isMain].drop(['isMain', 'backCateName'], axis=1)
goods = pd.read_csv(f'../milktea_good.csv')
data = pd.merge(goods, shops, on='shopid')
# drop_list = ['中杯', '叠加', '使用', '饮品', '兄弟', '招牌', '份', '书亦烧', '系列', '建议',
#             '单人', '套餐', '满杯', '双人', '大叔', '小姐姐', '网红', '快乐', '经典', '不知',
#              '特饮', '人气', '热饮', '特色', '必点', '双重', '热销', '全场', '通用', '代金券',
#              '张', '元', '使用', '兑换券', '餐', '汉堡', 'A', 'W', '适用', '仅', '堡', '鸡腿',
#              '热', '冰', 'WIFI','爆款', 'W34', '咖啡', 'L', '下午茶', '可', '只', '选', '提供',
#              '香辣', '大杯', '1000cc', '小料', 'WOW', '中', '阴阳师', '肯德基']


def generate_wordcloudlist():
    segments = []
    # text = ' '.join(goods.good)
    # words = pd.Series(jieba.cut(text, cut_all=False))
    # stopwords = set(words.value_counts().head(13).index)
    # for w in drop_list:
    #     stopwords.add(w)
    jieba.load_userdict(os.path.join(os.path.abspath(''), 'keyword.txt'))
    jieba.analyse.set_stop_words(os.path.join(os.path.abspath(''), 'stopword.txt'))
    for index, row in data.iterrows():
        content = row['good']
        # words = jieba.lcut(content, cut_all=False)
        words = jieba.analyse.extract_tags(content)
        for word in words:
            # if word not in stopwords:
            segments.append({'keyword': word, 'brand': row.title})

    result = pd.DataFrame(segments)
    result.to_csv('keywords3.csv')

    # seg_df = pd.DataFrame(segments)
    # word_df = seg_df.groupby('word')['count'].sum()
    # word_df = word_df.drop([' '])
    #
    # result = word_df.sort_values(ascending=False)


if __name__ == "__main__":
    generate_wordcloudlist()