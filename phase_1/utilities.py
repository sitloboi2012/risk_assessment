from __future__ import annotations
from logging import warning

import numpy as np
import pandas as pd
#from scipy import spatial


def post_processing_aibi_version(dataframe):
    dataframe["Audit Recommendation"] = dataframe["Audit Recommendation"].apply(lambda x: " ".join(map(str, x)))
    return dataframe

def post_processing_fssc_version_5(dataframe):
    dataframe = dataframe.drop(["Address", "Email"],axis=1)
    dataframe["Audit Type"] = dataframe["Audit Type"].apply(lambda x: x.replace("\n", " "))
    dataframe["Minor Nonconformities"] = dataframe["Minor Nonconformities"].apply(lambda x: sum([int(s) for s in x.split() if s.isdigit()]))

    try:
        organisation_name = dataframe["Organisation Name"].str.split("\n")[0][1]
        dataframe["Organisation Name"] = organisation_name.split(":")[1].strip()
    except IndexError:
        pass

    try:
        city_name = dataframe["City"].str.split("\n")[0][0]
        dataframe["City"] = city_name.split(":")[1].strip()
    except IndexError:
        pass

    try:
        region_name = dataframe["Region"].str.split("\n")[0][0]
        dataframe["Region"] = region_name.split(":")[1].strip()
    except IndexError:
        pass

    try:
        postal_name = dataframe["Postal Code"].str.split("\n")[0][0]
        dataframe["Postal Code"] = postal_name.split(":")[1].strip()
    except IndexError:
            pass

    return dataframe

def convert_to_dataframe(list_of_dictionaries):
    data = pd.DataFrame(columns= list(list_of_dictionaries[0].keys()))
    for i in list_of_dictionaries:
        data.append(i, ignore_index=True)
    return data

def image_vectorization(image: np.ndarray) -> np.ndarray:
    length, height, depth = image.shape
    return image.reshape((length * height * depth, 1))

#def distance_comparison(image_array, original_image_vector):
#    result_list = []
#    for array in original_image_vector:
#        result_list.append(1 - spatial.distance.cosine(image_array, array))
#    return np.argmax(result_list)

def preprocessing_dataframe(dataframe):
    dataframe["City"] = dataframe["City"].str.split(",")
    dataframe["City"] = dataframe["City"].str.get(0)
    dataframe["Organisation Name"] = dataframe["Organisation Name"].str.split("-")
    dataframe["Organisation Name"] = dataframe["Organisation Name"].str.get(0)
    dataframe["Organisation Name"] = dataframe["Organisation Name"].str.replace(",", " ")
    dataframe["Organisation Name"] = dataframe["Organisation Name"].str.replace(".", "")
    dataframe["Organisation Name"] = dataframe["Organisation Name"] + "-" + dataframe["City"]
    return dataframe

def cleaning_product_name(product_description):
    split_text = product_description.split(",")
    return split_text[0]