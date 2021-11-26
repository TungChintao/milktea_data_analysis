import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pyecharts.charts as pyc
import pyecharts.options as opts
import pyecharts.globals as glbs
from data_process.generate_chart import render
from sklearn import preprocessing as ppcs
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

shops = pd.read_csv('../milktea_shop.csv')
shops = shops.loc[shops.isMain == 1]
brands = shops[['title', 'avgprice', 'avgscore']]
brands = brands.groupby('title').mean().reset_index()
brands.avgprice = brands.avgprice.map(lambda x: round(x, 2))
brands.avgscore = brands.avgscore.map(lambda x: round(x, 2))
brands['counts'] = brands.title.map(dict(shops.title.value_counts()))
features = brands.drop('title', axis=1)


def write_js(file, locate, overwrite):
    with open(file, 'r') as f:
        html = f.read()
    with open(file, 'w') as f:
        f.write(html.replace(locate, overwrite))


# 可视化数据分布
def plot_features(df, title='', size=2):
    plt.figure(figsize=(10,5))
    for col in df.columns:
        plt.scatter(df.index, df[col], s=size, label=col, alpha=0.6)
    plt.legend(loc='upper right', markerscale=6)
    plt.title(title)
    plt.show()


def features_scaling(features, scaler, return_=False, show=False,method=''):
    scaler.fit(features)
    features_scaled = pd.DataFrame(scaler.transform(features), columns=features.columns)
    if show:
        plot_features(features_scaled, title='Features after ' + method)
    if return_:
        return (scaler, features_scaled)


# 各种特征放缩组合
def get_feature_dict(norm='l2'):
    _, scaled1 = features_scaling(features, ppcs.MinMaxScaler(), return_=True)
    _, scaled2 = features_scaling(features, ppcs.StandardScaler(), return_=True)
    _, scaled3 = features_scaling(features, ppcs.Normalizer(norm=norm), return_=True)
    _, scaled1_2 = features_scaling(scaled1, ppcs.StandardScaler(), return_=True)
    _, scaled2_3 = features_scaling(scaled2, ppcs.Normalizer(norm=norm), return_=True)
    _, scaled1_2_3 = features_scaling(scaled1_2, ppcs.Normalizer(norm=norm), return_=True)
    feature_dict = {
        'minmax': scaled1, 'standard': scaled2, 'normalize': scaled3,
        'minmax_standard': scaled1_2,
        'standard_normalize': scaled2_3,
        'minmax_standard_normalize': scaled1_2_3
    }
    return feature_dict


# 聚类-单个模型
def clustering(features, N, show=False):
    km = KMeans(n_clusters=N)
    km.fit(features)
    features['labels'] = km.labels_
    if show:
        for i in np.unique(km.labels_):
            plot_features(features.loc[features.labels==i], f'class-{i}')
    features.drop('labels', axis=1, inplace=True)
    return km


# 获取各类的数据观测
def get_clusters(model, feat=brands):
    feat['labels'] = model.labels_
    clusters = []
    for i in range(model.n_clusters):
        df = feat.loc[feat.labels==i].drop('labels', axis=1)
        clusters.append(df)
    feat.drop('labels', axis=1, inplace=True)
    return clusters


# 对应原始数据的聚类中心
def get_original_centers(model, brands=brands):
    clusters = get_clusters(model, feat=brands)
    centers = pd.DataFrame([df.drop('title', axis=1).mean() for df in clusters])
    return centers


# 绘制聚类散点图
def plot_clusters(km, score, feat, method, save_path=None):

    colors = ['#6D84A5', '#B50A24', '#F49F45', '#D6C7B0', '#73B9BC', '#F0DF7D', '#DA6964', '#6F9F71', '#FFCD41', '#4A393B']
    axis_opts = {
        "type": "value",
        "axisLabel": {"color": "#DDDEEE"},
        "nameTextStyle": {"color": "#DDDEEE"},
        "axisLine":{"lineStyle":{"color": "#889099"}},
        "splitLine": {"lineStyle": {"color": "#889099"}}
    }
    clusters = get_clusters(km, feat=feat)
    centers = pd.DataFrame(km.cluster_centers_, columns=['avgprice', 'avgscore', 'counts'])
    centers.index = ['No.' + str(idx+1) for idx in centers.index]
    original_centers = get_original_centers(km)
    original_centers.index = centers.index

    centers_tb = '\n\n ➤ Cluster Centers: \n\n ' + centers.to_markdown().replace('\n', '\n ').replace(':', '-')
    org_centers_tb = '\n\n ➤ Original Cluster Centers: \n\n ' + original_centers.to_markdown().replace('\n', '\n ').replace(':', '-')
    bar = '\n\n ➤ Clusters Counts: '
    brands_counts = [len(df) for df in clusters]
    for i, c in enumerate(centers.index):
        bar += f'\n\n [{c}] ' + '▆' * int(brands_counts[i]/150+1) + ' ' + str(brands_counts[i])

    scatter = pyc.Scatter3D(init_opts=opts.InitOpts(height='700px', width='100%', bg_color='#1a1c1d', theme=glbs.ThemeType.DARK))
    for i in range(km.n_clusters):
        data = [[float(v) for v in rows] for rows in clusters[i].values]
        scatter.add(
            f'Cluster No.{i+1}', data,
            itemstyle_opts=opts.ItemStyleOpts(color=colors[i]),
            xaxis3d_opts=dict(axis_opts, name='avgprice'),
            yaxis3d_opts=dict(axis_opts, name='avgscore'),
            zaxis3d_opts=dict(axis_opts, name='counts'),
            grid3d_opts=opts.Grid3DOpts(width=80, height=80, depth=80)
        )
    scatter.set_global_opts(
        # tooltip_opts=opts.TooltipOpts(is_show=False),
        title_opts=opts.TitleOpts(
            title=f' [ Scaling method: {method} ]',
            subtitle=f' ➤ Best Model: \n\n [ n_clusters = {km.n_clusters}, silhouette_score = {round(score, 4)} ]' + centers_tb + org_centers_tb + bar,
            title_textstyle_opts=opts.TextStyleOpts(color='#DDDEEE'),
            subtitle_textstyle_opts=opts.TextStyleOpts(color='#22DDEE', font_size=14 ,font_family='Courier New')
        ),
        legend_opts=opts.LegendOpts(pos_right='2%', pos_top='2%', orient='vertical'),
        # toolbox_opts=opts.ToolboxOpts(
        #     pos_left=None, pos_right='2%', pos_bottom='2%', orient='vertical',
        #     feature=opts.ToolBoxFeatureOpts()
        # )
    )
    render(scatter, changeHost=True)
    write_js('temp.html', '"type": "scatter3D",', '"type": "scatter3D","emphasis": {"itemStyle": {"color": "#00ffff"}},"symbolSize":6,')
    write_js('temp.html', '"grid3D": {', '"grid3D": {"axisPointer": {"lineStyle": {"color": "#22DDEE"}},')
    name = f'{method}-{km.n_clusters}-{round(score, 4)}.html'
    if save_path:
        os.rename('temp.html', save_path + '/' + name)
    else:
        print(name)
        input('\n任意键继续...\n')


# 绘制聚类雷达图
def plot_radar(i):
    radar = pyc.Radar(
        init_opts=opts.InitOpts(theme=glbs.ThemeType.DARK, width='100%', height='300px', bg_color='#1a1c1d')
    ).set_colors([colors[i]]
    ).add_schema(
        schema=[{"name": name, "max": 1, "min": -1} for name in ['消费水平', '店铺评分', '店铺数量']],
        shape='circle',
        center=["50%", "50%"],
        radius="80%",
        angleaxis_opts=opts.AngleAxisOpts(
            axistick_opts=opts.AxisTickOpts(is_show=False),
            axislabel_opts=opts.LabelOpts(is_show=False),
            axisline_opts=opts.AxisLineOpts(is_show=False),
            splitline_opts=opts.SplitLineOpts(is_show=False)
        ),
        radiusaxis_opts=opts.RadiusAxisOpts(
            min_=-1, max_=1, interval=0.5,
            splitarea_opts=opts.SplitAreaOpts(
                is_show=True,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5)
            )
        ),
        polar_opts=opts.PolarOpts(),
        splitarea_opt=opts.SplitAreaOpts(is_show=False),
        splitline_opt=opts.SplitLineOpts(is_show=False)
    ).add(
        series_name=f'{names[i]}：{quotes[i]}',
        data=[{'name': f'{names[i]}', "value": [round(v, 2) for v in centers[i]]}],
        areastyle_opts=opts.AreaStyleOpts(opacity=0.2),
        linestyle_opts=opts.LineStyleOpts(width=1)
    ).set_global_opts(
        legend_opts=opts.LegendOpts(pos_left='2%', pos_bottom='2%', )
    )
    render(radar)
    os.rename('temp.html', f"[modeling]{names[i].replace(' ', '-')}.html")


if __name__ == '__main__':
    start = time.time()
    feature_dict = get_feature_dict()
    score_dict = {k: [] for k in feature_dict.keys()}
    model_dict = {k: [] for k in feature_dict.keys()}
    RANGE = [2, 3, 4, 5, 6]

    for method, feature in feature_dict.items():
        print('-' * 60)
        for n in RANGE:
            print(f'processing {method}-scaled feature with {n}...')
            km = clustering(feature, n)
            score = silhouette_score(feature, km.labels_)
            score_dict[method].append(score)
            model_dict[method].append(km)
    print(f'------ Total cost {int(time.time() - start)} seconds ------')
    pd.DataFrame(score_dict).plot()
    plt.show()

    # 绘制三维散点分布（执行前先清空 save_path）
    # for method, models in model_dict.items():
    #     feat = feature_dict[method]
    #     for km, score in zip(models, score_dict[method]):
    #         plot_clusters(km, score, feat, method, save_path='./models')

    # # 选取模型（事先运行了上面的代码确定选取的模型）
    best = model_dict['standard_normalize'][1]
    clusters = get_clusters(best)
    #
    # # 输出各类数据观测采样
    for n, df in enumerate(clusters):
        df = df.reset_index(drop=True).sort_values(by='counts', ascending=False).head(20)
        data = [dict(df.iloc[i]) for i in range(len(df))]
        with open(f'cluster-{n + 1}.json', 'w', encoding='utf-8') as f:
            f.write(str(data).replace("'", '"').replace('{', '\n{'))
    #
    # # 绘制 best 模型的聚类雷达图
    centers = best.cluster_centers_
    names = ['Cluster No.1', 'Cluster No.2', 'Cluster No.3', 'Cluster No.4', 'Cluster No.5', 'Cluster No.6']
    colors = ['#6D84A5', '#B50A24', '#F49F45', '#D6C7B0', '#73B9BC', '#F0DF7D', '#DA6964', '#6F9F71']
    quotes = ['特征均衡', '低评分', '低消费', 'unknow', 'unknow', 'unknow']
    for i in range(best.n_clusters):
        plot_radar(i)

