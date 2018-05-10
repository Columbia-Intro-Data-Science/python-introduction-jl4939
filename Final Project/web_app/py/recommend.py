from sklearn import linear_model
from sklearn.neighbors import NearestNeighbors
import pandas as pd


def entry_variables(df, id_entry):
    col_labels = []
    if pd.notnull(df['类别'].iloc[id_entry]):
        for s in df['类别'].iloc[id_entry]:
            col_labels.append(s)
    return col_labels


def set_matrix(df, REF_VAR):
    for s in REF_VAR: df[s] = pd.Series([0 for _ in range(len(df))])
    colonnes = ['类别']
    for categorie in colonnes:
        for index, row in df.iterrows():
            if pd.isnull(row[categorie]): continue
            for s in row[categorie]:
                if s in REF_VAR: df.set_value(index, s, 1)
    return df


def cal_distance(df, id_entry):
    df_copy = df.copy(deep = True)

    #_____________________________________________________
    # Create additional variables to check the similarity
    variables = entry_variables(df_copy, id_entry)
    df_new = set_matrix(df_copy, variables)
    #____________________________________________________________________________________
    # determination of the closest neighbors: the distance is calculated / new variables
    X = df_new.as_matrix(variables)
    nbrs = NearestNeighbors(n_neighbors=31, algorithm='auto', metric='euclidean').fit(X)

    distances, indices = nbrs.kneighbors(X)
    xtest = df_new.iloc[id_entry].as_matrix(variables)
    xtest = xtest.reshape(1, -1)

    distances, indices = nbrs.kneighbors(xtest)

    return indices[0][:]


