#!/usr/bin/env python3
"""
STEP 2: Renderiza o vídeo (Voz + Imagens + Legenda)
"""
import os, json, requests, subprocess, asyncio
from edge_tts import Communicate

def get_audio(text):
    """Gera áudio com voz neural da Microsoft"""
    asyncio.run(Communicate(text, "pt-BR-FranciscaNeural").save("audio.mp3"))
    return "audio.mp3"

def download_broll(query):
    """Baixa vídeos de fundo (Pexels ou Pixabay)"""
    api_key = os.getenv("PEXELS_API_KEY")
    if api_key and api_key != "AGUARDANDO_NOVA_CHAVE":
        try:
            headers = {"Authorization": api_key}
            res = requests.get("https://api.pexels.com/videos/search", params={"query":query,"per_page":4,"orientation":"portrait","size":"medium"}, headers=headers, timeout=15)
            if res.status_code == 200:
                data = res.json()
                urls = [v["video_files"][0]["link"] for v in data.get("videos",[]) if v.get("video_files")]
                if urls:
                    for i,url in enumerate(urls): subprocess.run(["curl","-s","-o",f"clip_{i}.mp4",url],check=True)
                    print(f"✅ {len(urls)} clipes do Pexels")
                    return urls
        except: pass
    
    # Fallback (se não tiver Pexels)
    print("📥 Fallback Pixabay...")
    fallback = ["https://cdn.pixabay.com/video/2020/05/25/40130-424930043_large.mp4"]*4
    for i,url in enumerate(fallback): subprocess.run(["curl","-s","-o",f"clip_{i}.mp4",url],check=True)
    return fallback

def main():
    print("🎬 Renderizando...")
    with open("script.json") as f: script = json.load(f)
    full_text = f"{script['hook']}. {' '.join(script['body'])}. {script['cta']}"
    
    # 1. Gera Áudio
    audio = get_audio(full_text)
    
    # 2. Baixa Vídeos
    query = script["title"].split()[0] or "natureza"
    clips = download_broll(query)
    
    # 3. Junta tudo
    with open("list.txt","w") as f: f.writelines(f"file 'clip_{i}.mp4'\n" for i in range(len(clips)))
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i","list.txt","-i",audio,"-c:v","copy","-c:a","aac","-shortest","tmp.mp4"],check=True,capture_output=True)
    
    # 4. Legenda na tela
    subtitle = f"{script['hook']}\\n{' '.join(script['body'])}"
    subprocess.run(["ffmpeg","-y","-i","tmp.mp4","-vf",f"drawtext=text='{subtitle}':fontcolor=white:fontsize=24:x=(w-text_w)/2:y=h-100:box=1:boxcolor=black@0.6:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf,setsar=1,scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black","-c:a","copy","final.mp4"],check=True,capture_output=True)
    print("✅ Vídeo pronto: final.mp4")

if __name__ == "__main__":
    main()
