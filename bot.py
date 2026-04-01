import os
import time
import json
import firebase_admin
from firebase_admin import credentials, db
import urllib.request
import re

# 🌟 1. Firebase初期化
# GitHubのSecretsに保存したFIREBASE_KEY（JSON文字列）を読み込む
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

# HTMLを取得するための共通関数
def get_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"⚠️ アクセス失敗 ({url}): {e}")
        return ""

def collect():
    # 🔍 ターゲットに刺さるキーワード（日本人、韓国、中国、アニメ、コスプレ）
    # ここを増やすとバリエーションが広がるで！
    targets = ["日本人", "韓国", "chinese", "anime", "hentai", "コスプレ"]
    ref = db.reference('v_data/auto_videos')
    
    # 既存のURLをチェックして重複を避ける（任意）
    existing_data = ref.get()
    existing_urls = []
    if existing_data:
        existing_urls = [v['url'] for v in existing_data.values() if 'url' in v]

    for kw in targets:
        encoded_kw = urllib.parse.quote(kw)
        print(f"🚀 ジャンル 【{kw}】 を各サイトで探索中...")

        # --- 🎬 Pornhub セクション ---
        try:
            html = get_html(f"https://jp.pornhub.com/video/search?search={encoded_kw}")
            viewkeys = list(set(re.findall(r'viewkey=(ph[0-9a-f]+)', html)))
            for vk in viewkeys[:3]: # 各単語3件ずつ
                video_url = f"https://jp.pornhub.com/embed/{vk}"
                if video_url not in existing_urls:
                    ref.push({
                        'url': video_url,
                        'title': f"【{kw}】注目映像(PH)",
                        'author': "Premium_PH",
                        'timestamp': time.time()
                    })
                    print(f"✅ PH保存: {vk}")
        except: pass

        # --- 🎬 XVideos セクション ---
        try:
            html = get_html(f"https://www.xvideos.com/?k={encoded_kw}")
            v_ids = list(set(re.findall(r'video(\d+)', html)))
            for vid in v_ids[:3]:
                video_url = f"https://www.xvideos.com/embedframe/{vid}"
                if video_url not in existing_urls:
                    ref.push({
                        'url': video_url,
                        'title': f"【{kw}】激レア映像(XV)",
                        'author': "X_VIP",
                        'timestamp': time.time()
                    })
                    print(f"✅ XV保存: {vid}")
        except: pass

        # --- 🎬 xRoll セクション ---
        try:
            html = get_html(f"https://xroll.net/search/{encoded_kw}")
            xr_ids = list(set(re.findall(r'v/([a-zA-Z0-9]+)', html)))
            for xid in xr_ids[:3]:
                video_url = f"https://xroll.net/embed/{xid}"
                if video_url not in existing_urls:
                    ref.push({
                        'url': video_url,
                        'title': f"【{kw}】最新流出(XR)",
                        'author': "Roll_Master",
                        'timestamp': time.time()
                    })
                    print(f"✅ XR保存: {xid}")
        except: pass

        # サーバー負荷軽減のために少し待機
        time.sleep(2)

    # 🌟 最後にデータの整理
    clean_up(ref)

# 🧹 データベースを最大50件に保つ関数
def clean_up(ref):
    print("🧹 データベースの整理中（最大50件をキープ）...")
    data = ref.get()
    if data and len(data) > 50:
        # タイムスタンプ順（古い順）に並び替え
        items = sorted(data.items(), key=lambda x: x[1].get('timestamp', 0))
        # 50件を超える古い分を削除
        excess = len(data) - 50
        for i in range(excess):
            key_to_remove = items[i][0]
            ref.child(key_to_remove).delete()
            print(f"🗑️ 古いデータを整理したで: {key_to_remove}")

if __name__ == "__main__":
    print("🎬 Takeru Ultimate Video Bot 起動...")
    collect()
    print("✨ 全工程完了！お宝動画がFirebaseに詰まったで！")
