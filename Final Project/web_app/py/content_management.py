import pandas as pd

def Content():
    TEST_1 = ['Our group has 4 people.']
    return TEST_1

def All_data():
    df = pd.read_csv('/home/jl4939/mysite/static/data/data_cn_1950.csv', index_col=None)

    rank = []
    streamer = []
    platform = []
    category = []
    url = []

    for i in range(1950):
        rank.append(df.loc[i,'排名'])
        streamer.append(df.loc[i,'主播'])
        platform.append(df.loc[i,'平台'])
        category.append(df.loc[i,'类别'])
        url.append(df.loc[i,'直播间地址'])

    data_matrix = []
    data_matrix.append(rank)
    data_matrix.append(streamer)
    data_matrix.append(platform)
    data_matrix.append(category)
    data_matrix.append(url)

    return data_matrix