import os

MODEL_NAME = 'proken1'  # モデル名


"""データベース作成"""
DATABASE_SAVE_DIR = "../database_data"
DATABASE_SAVE_FILE_NAME = "database.tar"

MAX_SENTENCE_LENGTH = 25  # 1文の最大単語数 この値より長い文は使わない。

# コーパスファイル名
corpus_data_names = ["あるtweet2020-04-09", "あるtweet2020-04-10", "です。tweet2020-04-09", "です。tweet2020-04-10", "です。tweet2020-04-11", "です。tweet2020-04-13",
                        "ですよ！tweet2020-04-13", "ですよ！tweet2020-04-14", "私tweet2020-04-09", "私はtweet2020-04-11", "私はtweet2020-04-12"]


"""学習・会話モード共通項目------------------------------------------------------------------------------"""
MODEL_SAVE_DIR = "../trained_model_data/" + MODEL_NAME  # 学習モデルのセーブディレクトリ。

LOAD_MODEL_EPOCH_NUM = 27       # 途中から学習を始める際 or 会話モードで使う 学習済みモデルのエポック数。


"""学習モード----------------------------------------------------------------------------"""
IS_TRAIN_FROM_THE_MIDDLE = True    # 以前の続きから学習を再開するかどうか。


"""学習の調整用パラメータ。"""
EMBEDDING_DIM = 512
#LEARNING_RATE = 0.0001
CLIP = 50.0 # gradient clipping

# epoch, batch関連
MAX_EPOCH_NUM = 200  # エポック数
BATCH_SIZE = 64             # バッチサイズ