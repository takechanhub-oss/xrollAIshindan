import os
import time
import json
import firebase_admin
from firebase_admin import credentials, db
from ntscraper import Nitter

# 🌟 GitHubのSecret（FIREBASE_KEY）から鍵を読み込む
key_json = os.environ.get('FIREBASE_KEY')
if not key_json:
    print("❌ エラー: Secret 'FIREBASE_KEY' が設定されてへんで！")
    exit(1)

key_dict = json.loads(key_json)
cred = credentials.Certificate(key_dict)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://monitorsystem-cb31a-default-rtdb.firebaseio.com'
})

scraper = Nitter()

def collect():
    # 🔍 Xから動画を探すキーワード（自由に変えてや！）
    keywords = ["裏垢女子", "ハプニング", "拡散希望"] 
    ref = db.reference('online_chat/auto_videos')
    
    for kw in keywords:
        print(f"🚀 {kw} で動画を探索中...")
        try:
            # 安定性を考えて最新の10件を取得
            tweets = scraper.get_tweets(kw, mode='hashtag', number=10)
            for t in tweets['tweets']:
                if t['videos']:
                    # 動画の直リンク、タイトル、投稿者をFirebaseに送る
                    data = {
                        'url': t['videos'][0],
                        'title': t['text'][:100], 
                        'author': t['user']['name'],
                        'timestamp': time.time()
                    }
                    ref.push(data)
                    print(f"✅ 保存完了: {t['user']['name']} の動画")
        except Exception as e:
            print(f"❌ エラー発生: {e}")

if __name__ == "__main__":
    collect()
