import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import quote

# Ganti dengan kata kunci berita yang kamu cari
keyword = "PNM"
query = quote(keyword)
url = f"https://news.google.com/search?q={query}&hl=id&gl=ID&ceid=ID:id"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

results = []
for article in soup.select("article"):
    title_tag = article.find('a')
    time_tag = article.find('time')

    if title_tag:
        title = title_tag.text
        link = "https://news.google.com" + title_tag.get('href')[1:]

        # Ambil isi berita secara terpisah
        try:
            article_page = requests.get(link, headers=headers)
            article_soup = BeautifulSoup(article_page.text, 'html.parser')
            paragraphs = article_soup.find_all('p')
            content = ' '.join(p.text for p in paragraphs)
        except:
            content = ""

        date = time_tag['datetime'] if time_tag else ""

        results.append({
            "Judul": title,
            "Tanggal": date,
            "URL": link,
            "Isi": content
        })

df = pd.DataFrame(results)
df.to_excel("hasil_berita.xlsx", index=False)
print("Selesai! Berita disimpan di file 'hasil_berita.xlsx'")
