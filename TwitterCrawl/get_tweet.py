import re, sys, time, datetime
import json
import emoji
from socket import error as SocketError

import check_limit


FIRST_LOOP_START_TIME = 1288834974657


def tweet_id2time(tweet_id) :
    id_bin = bin(tweet_id>>22)
    tweet_time=int(id_bin,2)
    tweet_time += FIRST_LOOP_START_TIME
    return tweet_time


# ツイート本文の整形。
def screening(text) :
    s = text

    #RTを外す
    if s[0:3] == "RT " :
        s = s.replace(s[0:3],"")
    #@screen_nameを外す
    while s.find("@") != -1 :
        index_at = s.find("@")
        if s.find(" ") != -1  :
            index_sp = s.find(" ",index_at)
            if index_sp != -1 :
                s = s.replace(s[index_at:index_sp+1],"")
            else :
                s = s.replace(s[index_at:],"")
        else :
            s = s.replace(s[index_at:],"")

    #改行を外す
    while s.find("\n") != -1 :
        index_ret = s.find("\n")
        s = s.replace(s[index_ret],"")

    #URLを外す
    s = re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-…]+', "", s)
    #絵文字を「。」に置き換え その１
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), '。')
    s = s.translate(non_bmp_map)
    #絵文字を「。」に置き換え　その２
    s=''.join(c if c not in emoji.UNICODE_EMOJI else '。' for c in s  )

    #置き換えた「。」が連続していたら１つにまとめる
    while s.find('。。') != -1 :
        index_period = s.find('。。')
        s = s.replace(s[index_period:index_period+2],'。')

    #ハッシュタグを外す
    while s.find('#') != -1 :
        index_hash = s.find('#') 
        s = s[0:index_hash]

    return s


# 100ツイートの情報を受け取り、応答データを返す。
def getTweet(res,start_time,reset,session):
    res_text = json.loads(res.text)
    url1 = 'https://api.twitter.com/1.1/statuses/user_timeline.json'    #今回こちらは使わない
    url2 = 'https://api.twitter.com/1.1/statuses/lookup.json'

    cnt_req = 0
    max_tweet=start_time

    total_text = []                           # tweet本文（発話／応答）のリスト
    tweet_list = []                           # n_reply_to_status_idと応答tweetの対のリスト


    # 応答tweetを探す。
    for tweet in res_text['statuses']:
        status_id = tweet['in_reply_to_status_id_str']  # 発言tweetのid
        tweet_id=tweet['id']                  # 応答tweetのid

        if status_id != None :               # 当該tweetが応答かどうかの判断
            tweet_time = tweet_id2time(tweet_id)
            if tweet_time <= start_time :    # 前回処理より新しいtweetのみ処理する
                continue

            if max_tweet < tweet_time :
                max_tweet = tweet_time

            res_sentence = tweet['text']
            #RTを対象外にする
            if res_sentence[0:3] == "RT " :
                continue

            res_sentence = screening(res_sentence)
            if res_sentence == '' :
                continue

            tweet_list.append([status_id,res_sentence]) # 発言側idと応答文


    if len(tweet_list) == 0 :   # 1つも応答tweetが無かった時。
        return max_tweet,cnt_req ,total_text


    #複数status_idを連結する   
    id_list = tweet_list[0][0]
    for i in range(1,len(tweet_list)) :
        id_list += ','
        id_list += tweet_list[i][0]

    #--------------------------------------------------------------------------*
    #                                                                          *
    # 発話tweet抽出取得                                                        *
    #                                                                          *
    #--------------------------------------------------------------------------*   

    #複数status_id指定で発話tweet取得
    unavailableCnt = 0
    while True :
        try :
            req = session.get(url2, params = {'id':id_list ,'count':len(tweet_list)})   # 発言tweetの取得。
        except SocketError as e:
            print('ソケットエラー errno=',e.errno)
            if unavailableCnt > 10:
                raise

            check_limit.waitUntilReset(time.mktime(datetime.datetime.now().timetuple()) + 30)
            unavailableCnt += 1
            continue

        if req.status_code == 503:
            # 503 : Service Unavailable
            if unavailableCnt > 10:
                raise Exception('Twitter API error %d' % res.status_code)

            unavailableCnt += 1
            print ('Service Unavailable 503')
            check_limit.waitUntilReset(time.mktime(datetime.datetime.now().timetuple()) + 30)
            continue

        unavailableCnt = 0

        if req.status_code == 200 :
            req_text = json.loads(req.text)
            break
        else :
            raise Exception('Twitter API error %d' % res.status_code)    

    # 発話tweet本文スクリーニング
    for i in range(0,len(tweet_list)) :
        for j in range(0,len(req_text)) :
            if req_text[j]['id_str'] == tweet_list[i][0] :
                req_sentence = req_text[j]['text']

                if len(req_text) <= 0 :
                    print(req_text)
                    continue

                req_sentence = req_text[j]['text'] 
                #RTを対象外にする
                if req_sentence[0:3] == "RT " :
                    continue

                req_sentence = screening(req_sentence)

                #スクリーニングの結果、ブランクだったら対象外
                if req_sentence == '' :
                    continue   
                # 発話tweetと応答tweetを対で書き込み
                if req_sentence != tweet_list[i][1] :      
                    total_text.append("REQ:"+req_sentence)
                    total_text.append('RES:'+tweet_list[i][1])
                    cnt_req += 1

    max_tweet = max(max_tweet,start_time)
    return max_tweet,cnt_req ,total_text
