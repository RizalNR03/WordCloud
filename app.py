from flask import Flask, render_template, request
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Halaman utama untuk upload file
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Endpoint untuk menangani file upload dan mengembalikan kolom-kolom
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return {'error': 'No file part'}

    file = request.files['file']
    if file.filename == '':
        return {'error': 'No selected file'}

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        # Baca CSV dan ambil kolom header
        data = pd.read_csv(file_path)
        columns = data.columns.tolist()  # Ambil daftar kolom
        return {'columns': columns, 'file_path': file_path}

# Setelah memilih kolom, hasilkan WordCloud dan diagram batang
@app.route('/generate', methods=['POST'])
def generate_wordcloud():
    file_path = request.form['file_path']
    column_name = request.form['column_name']

    # Baca CSV
    data = pd.read_csv(file_path)

    # Gabungkan semua teks dari kolom yang dipilih
    text = ' '.join(data[column_name].dropna().astype(str))

    # Generate WordCloud
    wordcloud = WordCloud(width=800, height=400, background_color='white', max_words=200, colormap='rainbow').generate(text)
    
    # Simpan WordCloud ke file sementara
    wordcloud_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'wordcloud.png')
    wordcloud.to_file(wordcloud_image_path)

    # Hitung frekuensi kata untuk diagram batang
    words = text.split()
    word_freq = Counter(words)
    common_words = word_freq.most_common(10)

    # Plot diagram batang
    words, counts = zip(*common_words)
    plt.figure(figsize=(10, 6))
    plt.barh(words, counts, color='steelblue')
    plt.xlabel('Frequency')
    plt.title(f'Top 10 Words in {column_name}')
    plt.gca().invert_yaxis()
    
    # Simpan diagram batang ke file sementara
    bar_chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'barchart.png')
    plt.savefig(bar_chart_path)
    plt.close()

    return render_template('result.html', wordcloud_image_path=wordcloud_image_path, bar_chart_path=bar_chart_path)

if __name__ == '__main__':
    app.run(debug=True)
