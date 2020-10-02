import re

file_name = "jawiki.all_vectors.200d"


def load_File(file_name):
    file_data = []

    with open(file_name, "r", encoding="utf-8") as file:
        for sentence in file:
            file_data.append(sentence)   # rstripは改行コードを削除するため。
    
    return file_data

if __name__ == "__main__":
    input = load_File(file_name + ".txt")

    with open(file_name + "_sharp_trimmed.txt", "w", encoding="utf-8") as outFile:
        for sentence in input:
            sentence = re.sub("##", "", sentence)
            outFile.write(sentence)
