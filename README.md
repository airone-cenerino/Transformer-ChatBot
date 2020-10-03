# AIChatBot

## 参考にしたサイト
+ http://nlp.seas.harvard.edu/2018/04/03/attention.html (Transformerモデル)
+ https://qiita.com/gacky01/items/89c6c626848417391438 (リプライ対収集)
+ https://qiita.com/zincjp/items/e491f1712a701ad91a4f (MeCabの辞書追加)

## How to Use (ツイートの収集から会話まで)
1. /TwitterCrawl/private_key.pyというファイルを作成し、以下のように辞書型でTwitterAPIの鍵を記述する。

```
oath_key_dict = {
    "consumer_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "consumer_secret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "access_token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "access_token_secret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```


2. `/TwitterCrawl/twitter_crawler_main.py` を実行して、リプライ対を取得する。

3. `/Preprocessing/preprocess_twitter_data.py` の `data_file_names` を適宜変更してから実行して、前処理を行う。

4. `/TransformerModel/src/setting.py` のデータベース・辞書作成に関する項目を設定してから、`/TransformerModel/src/1database_dict_main.py` を実行して、データベースと辞書を作成する。

5. `/TransformerModel/src/2make_my_word2vec_corpus_main.py` を実行して、単語辞書のindex順に並んだWord2Vecのテキストファイルを作成する。

---

# コード解説
## Preprocessing
+ preprocess_twitter_data.py : Twitterから収集したリプライ対に下記3つの前処理を行う。

  1. 全角文字の置き換え
  2. 分かち書き
  3. Word2Vecにない単語を含む文の削除

---

## TwitterCrawl
TwitterAPIを用いて、会話データを収集する。(使う際は自分のAPIキーを辞書型に記述したprivate_key.pyを作成してください。)
  + check_limit.py : API呼び出しの回数制限関連。
  + get_tweet.py : ツイートを取得するメイン部分。
  + teitter_crawler_main.py : メイン関数

---

## Word2Vec
https://github.com/singletongue/WikiEntVec/releases からダウンロードしてきたWord2Vecのtxtファイルを加工する。
  + make_word_list.py : 存在する単語をリストにしてpickle化する。
  + trim_sharp.py : #文字を削除する。

---

## TransformerModel
コーパスデータを用いてseq2seqモデルの学習を行う。

### corpus_data
コーパスデータの置き場所。

### database_dict_data
データベースと辞書の保存場所。(git上にはないが、データベースと辞書を作れば生成されるフォルダ。)

### word2vec_corpus
自分の作成した単語辞書に合わせて作成するWord2Vecファイル置き場。

### src
  + 1database_dict_main.py : 単語の辞書とコーパスデータベースを作成する。
  + 2make_my_word2vec_corpus_main.py : 単語の辞書のindex順にword2vecのテキストファイルを作成する。
  + corpus_database.py : コーパスのデータベースを管理するクラス。
  + corpus_loader.py :  コーパスデータを読み込む。
  + database_dict_main.py : TransformerModel/corpus_dataのデータを読み込んで、データベース・辞書を作成するメイン関数。
  + database_dict_manager.py : データベースと辞書のを管理する。
  + setting.py : 設定
  + word_dict.py : 単語とインデックスの辞書を管理するクラス。