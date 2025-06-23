from flask import Flask, render_template, request, send_file
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import quote, urlparse
from datetime import datetime

app = Flask(__name__)

def extract_media_name(url):
    domain = urlparse(url).netloc.replace("www.", "")
    parts = domain.split('.')
    if len(parts) >= 2:
        return parts[-2] + '.' + parts[-1]
    return domain

def crawl_google_news(keyword, tanggal_mulai=None, tanggal_akhir=None):
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
            title = title_tag.text.strip()
            link = "https://news.google.com" + title_tag.get('href')[1:]

            # Ambil isi artikel
            try:
                article_page = requests.get(link, headers=headers)
                article_soup = BeautifulSoup(article_page.text, 'html.parser')
                paragraphs = article_soup.find_all('p')
                content = ' '.join(p.text for p in paragraphs)
            except:
                content = ""

            # Ambil nama media
            media = extract_media_name(link)

            # Filter waktu
            if time_tag and time_tag.has_attr('datetime'):
                try:
                    date_str = time_tag['datetime']
                    date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()

                    if tanggal_mulai and date_obj < tanggal_mulai:
                        continue
                    if tanggal_akhir and date_obj > tanggal_akhir:
                        continue

                    results.append({
                        "Judul": title,
                        "Tanggal": str(date_obj),
                        "Media": media,
                        "URL": link,
                        "Isi": content
                    })

                except:
                    continue

    df = pd.DataFrame(results)
    df.to_excel("hasil_berita_terfilter.xlsx", index=False)

    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    hasil = []
    keyword = ""
    tanggal_mulai = ""
    tanggal_akhir = ""
    jumlah_berita = None

    if request.method == 'POST':
        keyword = request.form.get('keyword')
        tanggal_mulai_str = request.form.get('tanggal_mulai')
        tanggal_akhir_str = request.form.get('tanggal_akhir')

        tgl_mulai = datetime.strptime(tanggal_mulai_str, "%Y-%m-%d").date() if tanggal_mulai_str else None
        tgl_akhir = datetime.strptime(tanggal_akhir_str, "%Y-%m-%d").date() if tanggal_akhir_str else None

        hasil = crawl_google_news(keyword, tgl_mulai, tgl_akhir)
        jumlah_berita = len(hasil)

        tanggal_mulai = tanggal_mulai_str
        tanggal_akhir = tanggal_akhir_str

    return render_template("index.html", hasil=hasil, keyword=keyword,
                           tanggal_mulai=tanggal_mulai,
                           tanggal_akhir=tanggal_akhir,
                           jumlah_berita=jumlah_berita)

@app.route('/unduh')
def unduh():
    return send_file("hasil_berita_terfilter.xlsx", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
