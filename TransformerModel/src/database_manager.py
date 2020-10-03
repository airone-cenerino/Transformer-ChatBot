import os
import torch
import corpus_database, corpus_loader, setting


# データベースのセーブ。
def save_database(database):
    directory = setting.DATABASE_SAVE_DIR

    if not os.path.exists(directory):
        os.makedirs(directory)

    torch.save({
        "corpus_database": database.__dict__,
    }, os.path.join(directory, setting.DATABASE_SAVE_FILE_NAME))


# データベースの作成。
def make_database():
    print("データベースを1から作り直します。")

    database = corpus_database.CorpusDatabase()     # データベース初期化
    data_pairs = corpus_loader.corpus_data_load()   # 会話ペアリストを取得。
    database.add_pairs(data_pairs)                  # データベースにデータを追加。
    save_database(database)                         # データベースをセーブする。



# 保存済みのデータベースをロードしてインスタンスを返す。
def load_database():
    database = corpus_database.CorpusDatabase()  # コーパスのデータベース初期化
    save_data = torch.load(os.path.join(setting.DATABASE_SAVE_DIR, setting.DATABASE_SAVE_FILE_NAME))

    # インスタンスに直接読み込ませる。
    database.__dict__ = save_data["corpus_database"]        

    print("データベースのロードに成功しました。")
    print()

    return database