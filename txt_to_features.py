from sklearn.feature_extraction.text import TfidfVectorizer


def txt_features(p_resumetxt, p_jdtxt):
    """
    This function returns TF-IDF features
    extracted from a list of texts
    :param p_resumetxt: preprocessed list of resume texts
    :param p_jdtxt: preprocessed list of job description texts
    :return: dataframe of features 
    """
    txt = p_resumetxt+p_jdtxt
    tv = TfidfVectorizer(max_df=0.85,min_df=1,ngram_range=(1,3))
    return tv.fit_transform(txt)

def feats_reduce(feats_df):

    """
    This function returns unreduced TF-IDF features.
    :param feats_df: features extracted from a list of texts
    :return: unreduced TF-IDF features
    """
    # Keep full TF-IDF features so small hackathon batches do not crash.
    return feats_df
