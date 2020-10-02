import pickle

load_file_name = "jawiki.all_vectors.200d_sharp_trimmed"
save_file_name = 'jawiki.200d.word_list.pickle'


def load_File(file_name):
    file_data = []

    with open(file_name, "r", encoding="utf-8") as file:
        for sentence in file:
            file_data.append(sentence)   # rstripは改行コードを削除するため。
    
    return file_data

if __name__ == "__main__":
    word_set = set()

    input = load_File(load_file_name + ".txt")

    for sentence in input:
        word_set.add(sentence.split(" ")[0])    # 単語のみ取り出し。
    
    with open(save_file_name, 'wb') as f:
        pickle.dump(word_set, f)