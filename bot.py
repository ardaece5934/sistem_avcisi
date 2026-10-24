import os
from flask import Flask
import requests
from bs4 import BeautifulSoup

TELEGRAM_BOT_TOKEN = "8768656855:AAGuP6dPJ_TU6o6Y7zTiNYzFbUerI4yc7AE"
TELEGRAM_CHAT_ID = "977052308"

HEDEF_ISLEMCILER = ["7800X3D", "7900X3D", "7950X3D", "7700", "7700X", "7600X", "7600", "7500F"]
HEDEF_EKRAN_KARTLARI = ["4070", "4070 SUPER", "4070 Ti", "4070 Ti SUPER", "4080 SUPER", "5060 Ti", "5070", "7800 XT", "7900 GRE", "7900 XT"]

SITELER = [
    {
        "isim": "Gaming.gen.tr",
        "url": "https://www.gaming.gen.tr/kategori/hazir-sistemler/",
        "kutu_class": "woocommerce-LoopProduct-link",
        "fiyat_class": "price"
    },
    {
        "isim": "İtopya",
        "url": "https://www.itopya.com/HazirSistemler",
        "kutu_class": "product",
        "fiyat_class": "product-price"
    },
    {
        "isim": "Sinerji",
        "url": "https://www.sinerji.gen.tr/hazir-sistemler-c-2116",
        "kutu_class": "product",
        "fiyat_class": "price"
    },
    {
        "isim": "İncehesap",
        "url": "https://www.incehesap.com/gaming-pc-fiyatlari/",
        "kutu_class": "card",
        "fiyat_class": "text-orange-500"
    }
]

app = Flask(__name__)

def telegram_mesaj_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mesaj}
    requests.post(url, json=payload)

def fiyat_kontrol_et():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for site in SITELER:
        try:
            response = requests.get(site['url'], headers=headers)
            soup = BeautifulSoup(response.content, "html.parser")
            sistemler = soup.find_all(class_=site["kutu_class"])
            
            for sistem in sistemler:
                tum_metin = sistem.text.upper() 
                fiyat_etiketi = sistem.find(class_=site["fiyat_class"])
                
                if not fiyat_etiketi: continue
                    
                ins_etiketi = fiyat_etiketi.find("ins")
                if ins_etiketi:
                    fiyat_metni = ins_etiketi.text
                else:
                    fiyat_metni = fiyat_etiketi.text
                    
                fiyat_metni = fiyat_metni.split(',')[0] 
                fiyat_metni = "".join(filter(str.isdigit, fiyat_metni))
                
                if fiyat_metni == "": continue
                    
                fiyat = int(fiyat_metni)

                if 45000 <= fiyat <= 80000:
                    islemci_uygun = any(islemci in tum_metin for islemci in HEDEF_ISLEMCILER)
                    gpu_uygun = any(gpu in tum_metin for gpu in HEDEF_EKRAN_KARTLARI)

                    if islemci_uygun and gpu_uygun:
                        mesaj = f"🚨 {site['isim']} İNDİRİM YAKALANDI!\n\nFiyat: {fiyat} TL\nLink: {site['url']}"
                        telegram_mesaj_gonder(mesaj)
                        print(f"İndirim bulundu: {site['isim']} - {fiyat} TL")
        except Exception as e:
            print(f"Hata ({site['isim']}): {e}")

@app.route('/')
def ana_sayfa():
    return "Sistem Avcısı 7/24 Aktif!"

@app.route('/tarama_tetikle')
def tarama_tetikle():
    fiyat_kontrol_et()
    return "Tarama tamamlandı."

@app.route('/test_et')
def test_et():
    rapor = "🛠️ CLASS TEST RAPORU 🛠️\n\n"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    for site in SITELER:
        try:
            response = requests.get(site['url'], headers=headers)
            soup = BeautifulSoup(response.content, "html.parser")
            ilk_sistem = soup.find(class_=site["kutu_class"])
            
            if ilk_sistem:
                fiyat_etiketi = ilk_sistem.find(class_=site["fiyat_class"])
                fiyat_metni = fiyat_etiketi.text.strip().replace('\n', ' ') if fiyat_etiketi else "Fiyat Bulunamadi"
                rapor += f"✅ {site['isim']} OK!\nOrnek Fiyat: {fiyat_metni[:25]}\n\n"
            else:
                rapor += f"❌ {site['isim']} HATA! Kutu bulunamadi.\n\n"
        except Exception as e:
            rapor += f"⚠️ {site['isim']} COKTU: {e}\n\n"
            
    telegram_mesaj_gonder(rapor)
    return "Test raporu Telegram'a gonderildi! Telefonuna bak."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
