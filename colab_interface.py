from IPython.display import HTML, display

def create_interface():
    display(HTML("""
    <div style="padding: 20px; background-color: #f5f5f5; border-radius: 10px;">
        <h3>YouTube Video İşleme ve Hugging Face'e Yükleme</h3>
        <p>1. Hugging Face token'ınızı girin</p>
        <p>2. YouTube URL'sini yapıştırın</p>
        <p>3. İşlemi başlatın</p>
    </div>
    """)) 