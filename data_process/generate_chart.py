import os
import pandas as pd
import pyecharts.charts as pyc
import pyecharts.options as opts
import pyecharts.globals as glbs


keywords = pd.read_csv('keywords2.csv')


def render(chart, temp=True, show=False, changeHost=False):
    '''custom render options'''
    if temp:
        filename = 'temp.html'
    else:
        try:
            filename = chart.options['title'].opts[0]['text'] + '.html'
        except:
            filename = 'unnamed.html'
    chart.render(filename)
    if changeHost:
        js_0= 'https://cdn.jsdelivr.net/npm/echarts@latest/dist/'
        js_1 = 'https://assets.pyecharts.org/assets/'
        with open(filename, 'r') as f:
            html = f.read().replace(js_0, js_1)
        with open(filename, 'w') as f:
            f.write(html)
    if show:
        os.system(f'start {filename}')


def generate_wordcloud():
    drop_list = ['1000cc', '小料', 'WOW', '中']

    counts = keywords.loc[keywords.keyword.map(lambda x: x not in drop_list)].keyword.value_counts()

    words = list(zip(list(counts.index), [int(n) for n in counts]))
    wc = pyc.WordCloud(
        init_opts=opts.InitOpts(theme=glbs.ThemeType.DARK, width='100%', height='360px', bg_color='#1a1c1d')
    ).add(
        '', words, word_size_range=(8, 88), shape=glbs.SymbolType.DIAMOND
    )
    render(wc, show=True, changeHost=True)


if __name__ == '__main__':
    generate_wordcloud()
