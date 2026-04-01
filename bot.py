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

key_dict = json.loads(key_json)
cred = credentials.Certificate(key_dict)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://faceidshindan-default-rtdb.firebaseio.com'
})

def get_html(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8', errors='ignore')

def collect():
    # 🔍 ターゲットに刺さる多国籍・アニメキーワード
    targets = ["日本人", "韓国", "chinese", "anime", "hentai", "コスプレ"]
    ref = db.reference('v_data/auto_videos')
    
    for kw in targets:
        encoded_kw = urllib.parse.quote(kw)
        print(f"🚀 【{kw}】 を各サイトで探索中...")

        # --- 🎬 Pornhub ---
        try:
            html = get_html(f"https://jp.pornhub.com/video/search?search={encoded_kw}")
            viewkeys = list(set(re.findall(r'viewkey=(ph[0-9a-f]+)', html)))
            for vk in viewkeys[:3]: # 各サイト3件ずつ
                ref.push({
                    'url': f"https://jp.pornhub.com/embed/{vk}",
                    'title': f"【{kw}】注目映像(PH)",
                    'author': "PH_Stream",
                    'timestamp': time.time()
                })
                print(f"✅ PH保存: {vk}")
        except: pass

        # --- 🎬 XVideos ---
        try:
            html = get_html(f"https://www.xvideos.com/?k={encoded_kw}")
            v_ids = list(set(re.findall(r'video(\d+)', html)))
            for vid in v_ids[:3]:
                ref.push({
                    'url': f"https://www.xvideos.com/embedframe/{vid}",
                    'title': f"【{kw}】極秘映像(XV)",
                    'author': "XV_Premium",
                    'timestamp': time.time()
                })
                print(f"✅ XV保存: {vid}")
        except: pass

        # --- 🎬 xRoll ---
        try:
            html = get_html(f"https://xroll.net/search/{encoded_kw}")
            xr_ids = list(set(re.findall(r'v/([a-zA-Z0-9]+)', html)))
            for xid in xr_ids[:3]:
                ref.push({
                    'url': f"https://xroll.net/embed/{xid}",
                    'title': f"【{kw}】新着(XR)",
                    'author': "XR_Vault",
                    'timestamp': time.time()
                })
                print(f"✅ XR保存: {xid}")
        except: pass

        time.sleep(3)

    # 🌟 2. 【安全装置】50件を超えたら古い順に削除
    clean_up(ref)

def clean_up(ref):
    print("🧹 データベースの整理中（最大50件キープ）...")
    data = ref.get()
    if data and len(data) > 50:
        # タイムスタンプ順に並び替え
        items = sorted(data.items(), key=lambda x: x[1].get('timestamp', 0))
        # 50件を超える分を削除
        excess = len(data) - 50
        for i in range(excess):
            key_to_remove = items[i][0]
            ref.child(key_to_remove).delete()
            print(f"🗑️ 古いデータを削除したで: {key_to_remove}")

if __name__ == "__main__":
    print("🎬 Takeru Ultimate Video Bot 起動...")
    collect()
    print("✨ 完了！Firebaseもスッキリさせたで！")
