import os
import json
from google import genai
from datetime import datetime

# Inisialisasi client Gemini menggunakan API Key dari Environment Variable GitHub Actions
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

DATA_PATH = "data/story.json"

def load_story_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"File {DATA_PATH} tidak ditemukan, Bosku!")
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_story_data(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_next_episode(story_data):
    bible = story_data["storyBible"]
    characters = story_data["characters"]
    episodes = story_data["episodes"]
    
    episode_number = len(episodes) + 1
    
    # Rangkuman episode terakhir untuk konteks kesinambungan cerita
    last_episode_summary = "Ini adalah awal mula cerita (Episode 1)."
    if episodes:
        last_ep = episodes[-1]
        last_episode_summary = f"Episode sebelumnya ({last_ep['title']}): {last_ep.get('summary', '')}"

    prompt = f"""
    Anda adalah penulis novel fantasi epik profesional. Buatlah **Episode {episode_number}** untuk semesta berikut:
    
    - Judul Universe: {bible['universeName']}
    - Genre: {bible['genre']}
    - Gaya Narasi: {bible['narratorStyle']}
    - Aturan Menulis: {bible['writingRules']}
    - Mekanisme Dunia: {json.dumps(bible['worldMechanics'], ensure_ascii=False)}
    - Karakter Aktif: {json.dumps(characters, ensure_ascii=False)}
    
    Kondisi Cerita Saat Ini:
    {last_episode_summary}
    
    Instruksi Khusus:
    - Panjang teks target sekitar {bible['episodeLength']} karakter.
    - Fokus pada ketegangan atmosferik, pertentangan antara Klan Lencana Perak Atas dan Bawah, serta penggunaan pedang perak dingin dan Dengung Giok.
    - Akhiri episode dengan ketegangan atau *cliffhanger* yang menarik untuk episode berikutnya.
    
    Berikan output dalam format JSON mentah (tanpa blok markdown tambahan ```json ... ``` agar mudah diparse) dengan struktur kunci berikut:
    {{
      "title": "Judul Episode yang Menarik",
      "summary": "Ringkasan 1-2 kalimat dari peristiwa penting di episode ini",
      "content": "Teks isi cerita lengkap di sini..."
    }}
    """

    print(f"Sedang meracik Episode {episode_number}...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    
    text_response = response.text.strip()
    # Bersihkan jika ada format markdown block
    if text_response.startswith("```json"):
        text_response = text_response[7:]
    if text_response.endswith("```"):
        text_response = text_response[:-3]
        
    new_ep_data = json.loads(text_response.strip())
    
    # Tambahkan metadata episode
    new_episode = {
        "episodeNumber": episode_number,
        "title": new_ep_data.get("title", f"Episode {episode_number}"),
        "summary": new_ep_data.get("summary", ""),
        "content": new_ep_data.get("content", ""),
        "createdAt": datetime.utcnow().isoformat() + "Z"
    }
    
    return new_episode

if __name__ == "__main__":
    data = load_story_data()
    
    # Buat episode baru
    new_ep = generate_next_episode(data)
    
    # Masukkan ke dalam array episodes
    data["episodes"].append(new_ep)
    data["storyBible"]["updatedAt"] = datetime.utcnow().isoformat() + "Z"
    
    # Simpan kembali
    save_story_data(data)
    print(f"Berhasil! Episode '{new_ep['title']}' sukses ditambahkan ke story.json, Bosku.")