import os
import time
import json
import firebase_admin
from firebase_admin import credentials, db
import urllib.request
import re
import random

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

def get_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com/"
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as response:
        return response.read().decode('utf-8', errors='ignore')

def collect():
    # 🔍 ターゲットキーワード
    targets = ["日本人", "韓国", "JK", "潮吹き", "パイパン", "オナニー", "愛液", "自撮り", "流出", "ハプニング", "女子大生"]
    
    # 🌟 検索モードをランダムで切り替えて、過去の名作も拾う！
    # mr:新着順, mv:閲覧数順, tr:高評価順
    modes = ["mr", "mv", "tr"]
    selected_mode = random.choice(modes)
    print(f"📡 今回のハントモード: {selected_mode}")

    ref = db.reference('v_data/auto_videos')
    existing_data = ref.get()
    existing_urls = []
    if existing_data:
        existing_urls = [v['url'] for v in existing_data.values() if 'url' in v]

    for kw in targets:
        encoded_kw = urllib.parse.quote(kw)
        # 🌟 モードをURLに反映！これで毎回違う動画がヒットする
        ph_url = f"https://jp.pornhub.com/video/search?search={encoded_kw}&o={selected_mode}"
        
        print(f"🚀 ジャンル 【{kw}】 をハント中...")
        try:
            html = get_html(ph_url)
            ids = list(set(re.findall(r'viewkey=(ph[0-9a-f]+)', html)))
            
            if not ids:
                print(f"⚠️ PH : 見つからんかったわ")
                continue

            # 🌟 各ワードから最大15本ブッコ抜く
            added_count = 0
            for vid in ids:
                if added_count >= 15: break
                v_url = f"https://jp.pornhub.com/embed/{vid}"
                if v_url not in existing_urls:
                    ref.push({
                        'url': v_url,
                        'title': f"【{kw}】厳選(PH)",
                        'author': "PH_Master",
                        'timestamp': time.time()
                    })
                    existing_urls.append(v_url)
                    added_count += 1
                    print(f"✅ 保存: {vid}")
            
        except Exception as e:
            print(f"❌ エラー: {e}")
        
        time.sleep(2)

    manage_storage(ref)

def manage_storage(ref):
    data = ref.get()
    if not data: return
    count = len(data)
    print(f"📊 現在のストック: {count}本")
    if count >= 1300:
        print("🚨 1300本到達！古い100本を掃除するわ。")
        items = sorted(data.items(), key=lambda x: x[1].get('timestamp', 0))
        for i in range(100):
            ref.child(items[i][0]).delete()
        print("🗑️ 整理完了！")

if __name__ == "__main__":
    collect()
