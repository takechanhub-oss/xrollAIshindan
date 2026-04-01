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
    print("❌ エラー: GitHubのSecret 'FIREBASE_KEY' が設定されてへんで！")
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

# HTML取得用の共通関数
def get_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"⚠️ アクセス失敗: {e}")
        return ""

def collect():
    # 🔍 ターゲットキーワード（たける指定の神ワード軍団！）
    targets = [
        "日本人", "韓国", "JK", "潮吹き", "パイパン", 
        "オナニー", "愛液", "自撮り", "流出", "ハプニング", "女子大生"
    ]
    
    ref = db.reference('v_data/auto_videos')
    
    # 🌟 重複防止用の既存URLリスト取得
    existing_data = ref.get()
    existing_urls = []
    if existing_data:
        existing_urls = [v['url'] for v in existing_data.values() if 'url' in v]

    for kw in targets:
        encoded_kw = urllib.parse.quote(kw)
        print(f"🚀 ジャンル 【{kw}】 をハント中...")

        # 🌟 ここが進化ポイント！
        # Pornhubは「&o=mr」(新着順)、XVideosは「&sort=uploaddate」をつけて、
        # 常に誰も見たことない最新の動画を引っ張ってくるようにしたで！
        sites = [
            {"name": "PH", "url": f"https://jp.pornhub.com/video/search?search={encoded_kw}&o=mr", "re": r'viewkey=(ph[0-9a-f]+)', "prefix": "https://jp.pornhub.com/embed/"},
            {"name": "XV", "url": f"https://www.xvideos.com/?k={encoded_kw}&sort=uploaddate", "re": r'video(\d+)', "prefix": "https://www.xvideos.com/embedframe/"},
            {"name": "XR", "url": f"https://xroll.net/search/{encoded_kw}", "re": r'v/([a-zA-Z0-9]+)', "prefix": "https://xroll.net/embed/"}
        ]

        for site in sites:
            try:
                html = get_html(site["url"])
                ids = list(set(re.findall(site["re"], html)))
                
                # 🌟 さらに進化ポイント！ 4件 -> 10件に大増量！
                for vid in ids[:10]: 
                    v_url = f"{site['prefix']}{vid}"
                    if v_url not in existing_urls:
                        ref.push({
                            'url': v_url,
                            'title': f"【{kw}】最新({site['name']})",
                            'author': f"{site['name']}_Master",
                            'timestamp': time.time()
                        })
                        # ターンの重複も防止
                        existing_urls.append(v_url)
                        print(f"✅ {site['name']}保存: {vid}")
            except: pass
        
        time.sleep(2) # サーバーを怒らせないための休憩

    # 🌟 2. データベースのメンテナンス（1300本の壁）
    manage_storage(ref)

def manage_storage(ref):
    data = ref.get()
    if not data: return
    
    count = len(data)
    print(f"📊 現在のストック: {count}本")
    
    # 🌟 1300本超えたら古い100本を抹消
    if count >= 1300:
        print("🚨 1300本到達！古い動画100本をシュートするわ。")
        items = sorted(data.items(), key=lambda x: x[1].get('timestamp', 0))
        
        for i in range(100):
            key_to_delete = items[i][0]
            ref.child(key_to_delete).delete()
        
        print("🗑️ メンテナンス完了。スッキリ整理したで！")

if __name__ == "__main__":
    print("🎬 Takeru Ultimate Collector V4 (Max Power Edition) 起動...")
    collect()
    print("✨ 全ミッション完了や！")
