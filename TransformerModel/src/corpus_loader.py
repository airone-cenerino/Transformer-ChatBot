import setting


# コーパスを読み込んでリストを返す。
def load_File(file_name):
    datafile_path = "../corpus_data/"  # データファイルが置いてあるディレクトリ

    file_data = []

    with open(datafile_path + file_name, "r", encoding="utf-8") as file:
        for sentence in file:
            file_data.append(sentence.rstrip())   # rstripは改行コードを削除するため。
    
    return file_data


def sentence2pairs(input, output):
    pairs = []
    for i in range(len(input)):
        pairs.append([input[i].split(" "), output[i].split(" ")])

    return pairs


def trim_long_sentence(pairs):
    filtered_pairs = []
    filtered_pair_num = 0

    for pair in pairs:
        # 長さが指定語以上の文はpairsに追加しない。
        if max(len(pair[0]), len(pair[1])) > setting.MAX_SENTENCE_LENGTH:
            filtered_pair_num += 1
            continue
        
        
        filtered_pairs.append([''.join(pair[0]), ''.join(pair[1])])
    
    return filtered_pairs, filtered_pair_num


def get_trimmed_pairs(file_name):
    input_file_name = file_name + "_preprocessed_input.txt"
    output_file_name = file_name + "_preprocessed_output.txt"

    input = load_File(input_file_name)  # 文のリスト(分かち済み)
    output = load_File(output_file_name)

    data_pairs = sentence2pairs(input, output)
    data_pairs, filtered_pair_num = trim_long_sentence(data_pairs)
    print(file_name + "の取り込みが完了しました。")
    print()

    return data_pairs, filtered_pair_num


def corpus_data_load():
    """
    会話対を読み込んで入力と応答がペアになっているデータを返す。
    型 : リスト(単語)のリスト(ペア)のリスト(複数応答)
    """

    print("------コーパスデータのロードを開始します。------")

    data_pairs = []
    filtered_pair_num = 0

    for corpus_name in setting.corpus_data_names:   # 順番にコーパスファイルを読み込む。
        pairs, num = get_trimmed_pairs(corpus_name)
        data_pairs.extend(pairs)
        filtered_pair_num += num

    print()
    print("登録されたペア数は" + str(len(data_pairs)) + "です。")
    print("上限単語数の" + str(setting.MAX_SENTENCE_LENGTH) + "語を超えて、省かれたペア数は" + str(filtered_pair_num) + "です。")

    print("------コーパスデータのロードが終了しました。------")
    print()

    return data_pairs