from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def cosine_sim(file_path1, file_path2):
    # 读取两个文件的内容
    with open(file_path1, "r", encoding="utf-8") as f1, open(file_path2, "r", encoding="utf-8") as f2:
        text1 = f1.read()
        text2 = f2.read()

    # 将文本转换为TF-IDF向量
    vectorizer = TfidfVectorizer().fit_transform([text1, text2])
    vectors = vectorizer.toarray()

    # 计算余弦相似度
    similarity = cosine_similarity(vectors)[0][1]
    return similarity

