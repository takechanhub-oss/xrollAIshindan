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
    print("❌ エラー: FIREBASE_KEY 設定なし")
    exit(1)

try:
    key_dict = json.loads(key_json)
    cred = credentials.Certificate(key_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://faceidshindan-default-rtdb.firebaseio.com'
    })
except Exception as e:
    print(f"❌ Firebaseエラー: {e}")
    exit(1)

def get_html(url):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
        "Referer": "https://www.google.com/",
        "Cookie": f"platform=pc; bs={random.getrandbits(32)};"
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as response:
        return response.read().decode('utf-8', errors='ignore')

def collect():
    targets = ["日本人", "韓国", "JK", "潮吹き", "パイパン", "オナニー", "愛液", "自撮り", "流出", "ハプニング", "女子大生"]
    random.shuffle(targets)

    modes = ["mr", "mv", "tr"]
    selected_mode = random.choice(modes)
    
    # 🌟 ここがV10の超進化ポイント！「1〜15ページ目」のどこかをランダムで開く！
    page_num = random.randint(1, 15)
    print(f"📡 潜入モード: {selected_mode} (ページ: {page_num})")

    ref = db.reference('v_data/auto_videos')
    existing_data = ref.get()
    existing_urls = []
    if existing_data:
        existing_urls = [v['url'] for v in existing_data.values() if 'url' in v]

    for kw in targets:
        encoded_kw = urllib.parse.quote(kw)
        
        # 🌟 URLに page=◯ を追加して奥深くを探るで！
        ph_url = f"https://jp.pornhub.com/video/search?search={encoded_kw}&o={selected_mode}&page={page_num}"
        
        print(f"🚀 【{kw}】 ハント開始...")
        try:
            html = get_html(ph_url)
            ids = list(set(re.findall(r'viewkey=(ph[0-9a-f]+)', html)))
            
            if not ids:
                print(f"⚠️ ヒットなし（ページ深すぎたかも）")
                continue

            added = 0
            for vid in ids:
                if added >= 12: break
                v_url = f"https://jp.pornhub.com/embed/{vid}"
                if v_url not in existing_urls:
                    ref.push({
                        'url': v_url,
                        'title': f"【{kw}】厳選(PH)",
                        'author': "PH_System",
                        'timestamp': time.time()
                    })
                    existing_urls.append(v_url)
                    added += 1
                    print(f"✅ 追加: {vid}")
            
            if added == 0:
                print(f"⏩ 全部持ってたからスキップや！")

            wait_time = random.uniform(4, 10)
            print(f"💤 次の検索まで {wait_time:.1f}秒 待機中...")
            time.sleep(wait_time)

        except Exception as e:
            print(f"❌ 警告: {e}")
            time.sleep(10)

    manage_storage(ref)

def manage_storage(ref):
    data = ref.get()
    if not data: return
    count = len(data)
    print(f"📊 ストック合計: {count}本")
    if count >= 1300:
        items = sorted(data.items(), key=lambda x: x[1].get('timestamp', 0))
        for i in range(100):
            ref.child(items[i][0]).delete()
        print("🗑️ 整理完了")

if __name__ == "__main__":
    collect()
