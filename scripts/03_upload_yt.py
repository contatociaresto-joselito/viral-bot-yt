#!/usr/bin/env python3
"""
STEP 3: Upload para YouTube via API oficial
Sempre como PRIVADO para você revisar antes de publicar
"""
import os, json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def main():
    # Verifica credenciais
    for env in ["YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"]:
        if not os.getenv(env):
            print(f"❌ {env} não configurada. Pulando upload.")
            return
    
    print("📤 Fazendo upload para YouTube...")
    
    # Configura OAuth
    creds = Credentials(
        token=None,
        refresh_token=os.getenv("YT_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("YT_CLIENT_ID"),
        client_secret=os.getenv("YT_CLIENT_SECRET"),
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )
    
    yt = build("youtube", "v3", credentials=creds)
    
    # Lê o roteiro
    with open("script.json", "r", encoding="utf-8") as f:
        script = json.load(f)
    
    # Upload
    request = yt.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": script["title"],
                "description": f"{script['hook']}\n\n{' '.join(script['body'])}\n\n{script['cta']}\n\n{' '.join(script['hashtags'])}",
                "tags": script["hashtags"],
                "categoryId": "22"
            },
            "status": {
                "privacyStatus": "private",  # 🔒 PRIVADO para revisão
                "selfDeclaredMadeForKids": False
            }
        },
        media_body=MediaFileUpload("final.mp4", mimetype="video/mp4")
    )
    
    response = request.execute()
    video_id = response["id"]
    
    print(f"✅ Upload concluído!")
    print(f"🎬 ID: {video_id}")
    print(f"🔗 Link: https://studio.youtube.com/video/{video_id}/edit")
    print(f"🔒 Status: PRIVADO → Mude para 'Público' após revisar")

if __name__ == "__main__":
    main()
