import os
import time
import json
import firebase_admin
from firebase_admin import credentials, db
from ntscraper import Nitter

# 🌟 GitHubのSecretから鍵を読み込む
key_dict = json.loads(os.environ.get('FIREBASE_KEY'))
cred = credentials.Certificate(key_dict)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://monitorsystem-cb31a-default-rtdb.firebaseio.com'
})

scraper = Nitter()

def collect():
    # Xから動画を探す（トレンド系やR18系など）
    keywords = ["裏垢", "拡散希望", "ハプニング"] 
    ref = db.reference('online_chat/auto_videos')
    
    for kw in keywords:
        print(f"🔍 探索中: {kw}")
        try:
            # 安定性を考えて少なめに取得
            tweets = scraper.get_tweets(kw, mode='hashtag', number=10)
            for t in tweets['tweets']:
                if t['videos']:
                    # 重複チェック（URLですでに登録されてないか）
                    data = {
                        'url': t['videos'][0],
                        'title': t['text'][:100], # 長すぎるとFirebaseが重くなるからカット
                        'author': t['user']['name'],
                        'timestamp': time.time()
                    }
                    ref.push(data)
                    print(f"✅ 発見: {t['user']['name']}")
        except Exception as e:
            print(f"❌ エラー: {e}")

if __name__ == "__main__":
    collect()
