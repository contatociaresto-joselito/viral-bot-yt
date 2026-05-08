#!/usr/bin/env python3
"""
STEP 1: Busca tendências do YouTube + Gera roteiro viral com Groq (Llama 3)
"""
import os, json, requests
from groq import Groq

def fetch_trends():
    """Busca vídeos em alta no YouTube (BR)"""
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("⚠️  YOUTUBE_API_KEY não configurada. Usando fallback...")
        return ["curiosidades", "você sabia", "fatos incríveis"]
    
    try:
        res = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "part": "snippet",
                "chart": "mostPopular",
                "regionCode": "BR",
                "maxResults": 8,
                "key": api_key
            },
            timeout=10
        )
        if res.status_code == 200:
            data = res.json()
            return [v["snippet"]["title"] for v in data.get("items", [])]
        else:
            print(f"⚠️  Erro YouTube API: {res.status_code}. Usando fallback...")
            return ["curiosidades", "você sabia", "fatos incríveis"]
    except Exception as e:
        print(f"⚠️  Falha ao buscar tendências: {e}. Usando fallback...")
        return ["curiosidades", "você sabia", "fatos incríveis"]

def main():
    print("🔍 Buscando tendências...")
    trends = fetch_trends()
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY não configurada. Pare.")
        exit(1)
    
    client = Groq(api_key=api_key)
    
    prompt = f"""Crie um roteiro de 35-45s para YouTube Shorts.
Nicho: curiosidades/viral
Tendências atuais: {', '.join(trends)}

Retorne APENAS JSON válido, sem markdown:
{{
  "title": "Título chamativo (máx 60 chars)",
  "hook": "Frase impactante dos primeiros 3 segundos",
  "body": ["Ponto 1", "Ponto 2", "Ponto 3"],
  "cta": "Chamada para ação final",
  "hashtags": ["#viral", "#shorts", "#fyp", "#curiosidades"]
}}

Regras:
- Hook forte 0-3s
- Linguagem direta, coloquial
- Sem explicações, só o JSON"""

    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=500
        )
        raw = res.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.replace("```json", "").replace("```", "").strip()
        
        script = json.loads(raw)
        
        # Validação mínima
        for field in ["title", "hook", "body", "cta", "hashtags"]:
            if field not in script:
                script[field] = "Conteúdo não disponível" if field != "body" else ["Ponto 1", "Ponto 2", "Ponto 3"]
        
        with open("script.json", "w", encoding="utf-8") as f:
            json.dump(script, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Roteiro gerado: {script['title']}")
        
    except Exception as e:
        print(f" Erro na IA: {e}")
        # Fallback script
        fallback = {
            "title": "5 Fatos Que Você Não Sabia",
            "hook": "Isso vai mudar sua visão sobre tudo!",
            "body": ["Fato 1 surpreendente", "Fato 2 que ninguém conta", "Fato 3 que vai te chocar"],
            "cta": "Gostou? Segue pra mais!",
            "hashtags": ["#viral", "#shorts", "#fyp", "#curiosidades"]
        }
        with open("script.json", "w", encoding="utf-8") as f:
            json.dump(fallback, f, ensure_ascii=False, indent=2)
        print("✅ Usando roteiro fallback")

if __name__ == "__main__":
    main()
