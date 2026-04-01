import os
import time
import json
import firebase_admin
from firebase_admin import credentials, db
from ntscraper import Nitter

# 🌟 1. GitHubのSecretから鍵を読み込む
key_json = os.environ.get('FIREBASE_KEY')
if not key_json:
    print("❌ エラー: Secret 'FIREBASE_KEY' が設定されてへんで！")
    exit(1)

try:
    key_dict = json.loads(key_json)
    cred = credentials.Certificate(key_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://faceidshindan-default-rtdb.firebaseio.com'
    })
except Exception as e:
    print(f"❌ Firebase初期化エラー: {e}")
    exit(1)

# 🌟 修正ポイント：サーバーを直接指定（動いてる確率が高いものを入れる）
scraper = Nitter()
instances = ["https://nitter.net", "https://nitter.cz", "https://nitter.it", "https://nitter.privacydev.net"]

def collect():
    keywords = ["裏垢女子", "自撮り界隈", "えちえち", "ハプニング", "マン凸"] 
    ref = db.reference('v_data/auto_videos')
    
    existing_videos = ref.get()
    existing_urls = []
    if existing_videos:
        existing_urls = [v['url'] for v in existing_videos.values() if 'url' in v]

    for kw in keywords:
        print(f"🚀 【{kw}】 で動画を探索中...")
        success = False
        
        # 🌟 複数のサーバーを試すループ
        for instance in instances:
            try:
                # 特定のサーバーを使って取得
                tweets = scraper.get_tweets(kw, mode='term', number=10, instance=instance)
                
                if tweets['tweets']:
                    for t in tweets['tweets']:
                        if t['videos'] and t['videos'][0] not in existing_urls:
                            data = {
                                'url': t['videos'][0],
                                'title': t['text'][:100].replace('\n', ' '),
                                'author': t['user']['name'],
                                'timestamp': time.time()
                            }
                            ref.push(data)
                            existing_urls.append(t['videos'][0])
                            print(f"✅ 保存完了: {t['user']['name']} (via {instance})")
                    success = True
                    break # 1つのサーバーで成功したら次のキーワードへ
            except Exception as e:
                print(f"⚠️ {instance} はダメやった: {e}")
                continue # 次のサーバーを試す

        if not success:
            print(f"❌ 【{kw}】 は全サーバーで全滅や...")
        
        time.sleep(2)

if __name__ == "__main__":
    print("🎬 Takeru Video Bot 起動...")
    collect()
    print("✨ 探索終了！")
