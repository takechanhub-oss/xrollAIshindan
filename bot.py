import os
import time
import json
import firebase_admin
from firebase_admin import credentials, db
import urllib.request
import re

# 🌟 1. Firebase初期化
key_json = os.environ.get('FIREBASE_KEY')
if not key_json:
    print("❌ エラー: FIREBASE_KEY が設定されてへんで！")
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

def collect():
    # 🔍 Pornhubでヒットしやすいエロキーワード
    keywords = ["素人", "自撮り", "ハプニング", "日本人", "流出"] 
    ref = db.reference('v_data/auto_videos')
    
    for kw in keywords:
        print(f"🚀 Pornhubで 【{kw}】 を探索中...")
        try:
            # Pornhubの検索ページURL（日本語版）
            search_url = f"https://jp.pornhub.com/video/search?search={urllib.parse.quote(kw)}"
            # 人間がアクセスしてるように見せかける
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
            req = urllib.request.Request(search_url, headers=headers)
            
            with urllib.request.urlopen(req) as response:
                html = response.read().decode('utf-8')
                
                # 正規表現で viewkey (動画ID) を引っこ抜く！
                viewkeys = re.findall(r'viewkey=(ph[0-9a-f]+)', html)
                
                if viewkeys:
                    # 重複を消して、最新の3件だけ保存する
                    for vk in list(set(viewkeys))[:3]:
                        # Pornhubの埋め込み用URL (自動再生＆ミュート設定には対応してないことが多いからシンプルに)
                        video_url = f"https://jp.pornhub.com/embed/{vk}"
                        
                        data = {
                            'url': video_url,
                            'title': f"【{kw}】の極秘動画",
                            'author': "Pornhub_Stream",
                            'timestamp': time.time()
                        }
                        ref.push(data)
                        print(f"✅ 保存完了: Pornhub ID [{vk}]")
                else:
                    print(f"⚠️ {kw} の動画が見つからんかったわ...")

        except Exception as e:
            print(f"❌ エラー発生: {e}")
        
        # 連続アクセスでブロックされないように少し長めに待つ
        time.sleep(3)

if __name__ == "__main__":
    print("🎬 Takeru Video Bot (Pornhub Edition) 起動...")
    collect()
    print("✨ 探索終了！")
