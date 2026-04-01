import os
import time
import json
import firebase_admin
from firebase_admin import credentials, db
from ntscraper import Nitter

# 🌟 1. GitHubのSecret（FIREBASE_KEY）から鍵を読み込む
key_json = os.environ.get('FIREBASE_KEY')
if not key_json:
    print("❌ エラー: Secret 'FIREBASE_KEY' が設定されてへんで！")
    exit(1)

try:
    key_dict = json.loads(key_json)
    cred = credentials.Certificate(key_dict)
    # 🌟 2. Firebase初期化（faceidshindan プロジェクト）
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://faceidshindan-default-rtdb.firebaseio.com'
    })
except Exception as e:
    print(f"❌ Firebase初期化エラー: {e}")
    exit(1)

scraper = Nitter()

def collect():
    # 🔍 ターゲットに刺さる検索キーワード（さらに増強！）
    keywords = ["裏垢女子", "自撮り界隈", "えちえち", "ハプニング", "女子高生", "バズれ", "マン凸", "パイ凸"] 
    
    # 🌟 保存先を 'v_data/auto_videos' に変更（スッキリ！）
    ref = db.reference('v_data/auto_videos')
    
    # 重複保存を防ぐために現在のURLリストを取得（オプション）
    existing_videos = ref.get()
    existing_urls = []
    if existing_videos:
        existing_urls = [v['url'] for v in existing_videos.values() if 'url' in v]

    for kw in keywords:
        print(f"🚀 【{kw}】 で動画を探索中...")
        try:
            # mode='term' にすることでハッシュタグ以外も広く拾えるようにする
            tweets = scraper.get_tweets(kw, mode='term', number=15)
            
            for t in tweets['tweets']:
                # 動画があって、かつ過去に保存してないURLなら保存
                if t['videos'] and t['videos'][0] not in existing_urls:
                    data = {
                        'url': t['videos'][0],
                        'title': t['text'][:100].replace('\n', ' '), # 改行を消してスッキリ
                        'author': t['user']['name'],
                        'timestamp': time.time()
                    }
                    ref.push(data)
                    existing_urls.append(t['videos'][0]) # 今回保存した分も重複チェックに追加
                    print(f"✅ 保存完了: {t['user']['name']} (@{t['user']['username']})")
                
                # 負荷軽減のため少し待つ
                time.sleep(1)
                
        except Exception as e:
            print(f"❌ 【{kw}】 の探索中にエラー: {e}")

if __name__ == "__main__":
    print("🎬 Takeru Video Bot 起動...")
    collect()
    print("✨ すべての探索が完了したで！")
