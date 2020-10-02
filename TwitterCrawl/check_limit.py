import json, datetime, time, sys
from socket import error as SocketError


# sleep処理　wait_finish_timeまで待機。
def waitUntilReset(wait_finish_time):
    seconds = wait_finish_time - time.mktime(datetime.datetime.now().timetuple())   # 待機時間の計算
    seconds = max(seconds, 0)
    print ('\n     =====================')
    print ('     == waiting %d sec ==' % seconds)
    print ('     =====================')
    sys.stdout.flush()
    time.sleep(seconds + 10)  # 念のため + 10 秒


# 回数制限に関するJsonを受け取り、残りの回数と回復する時刻を返す。
def getLimitContext(res_text):
    # searchの制限情報
    remaining_search = res_text['resources']['search']['/search/tweets']['remaining']
    reset1 = res_text['resources']['search']['/search/tweets']['reset']
    
    # lookupの制限情報
    remaining_user = res_text['resources']['statuses']['/statuses/lookup']['remaining']
    reset2 = res_text['resources']['statuses']['/statuses/lookup']['reset']
    
    # 制限情報取得の制限情報
    remaining_limit = res_text['resources']['application']['/application/rate_limit_status']['remaining']
    reset3     = res_text['resources']['application']['/application/rate_limit_status']['reset']

    return int(remaining_search), int(remaining_user), int(remaining_limit) , max(int(reset1),int(reset2),int(reset3))


# 回数制限を問合せ、アクセス可能になるまで wait する 
def checkLimit(session):
    url = "https://api.twitter.com/1.1/application/rate_limit_status.json"  # 回数制限を確認するエンドポイント。

    while True:
        unavailableCnt = 0

        try :
            res = session.get(url)  # 情報の取得。
        except SocketError as e:
            print('erron=',e.errno)
            print('ソケットエラー')
            if unavailableCnt > 10:
                raise

            waitUntilReset(time.mktime(datetime.datetime.now().timetuple()) + 30)
            unavailableCnt += 1
            continue

        if res.status_code == 503:
            # 503 : Service Unavailable
            if unavailableCnt > 10:
                raise Exception('Twitter API error %d' % res.status_code)

            unavailableCnt += 1
            print ('Service Unavailable 503')
            waitUntilReset(time.mktime(datetime.datetime.now().timetuple()) + 30)
            continue

        if res.status_code != 200:
            raise Exception('Twitter API error %d' % res.status_code)


        remaining_search, remaining_user, remaining_limit, reset = getLimitContext(json.loads(res.text))  # 残り回数と回復時刻の取得。
        
        if remaining_search <= 1 or remaining_user <=1 or remaining_limit <= 1:
            waitUntilReset(reset+30)    # どれか一つでも回数制限が無ければ回復するまで待機。
        else :
            break

    sec = reset - time.mktime(datetime.datetime.now().timetuple())
    print("残り回数:",remaining_search,",",remaining_user, ",",remaining_limit ," 残り時間:",sec)
    return reset