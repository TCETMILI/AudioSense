# 🎵 AudioSense

**AudioSense**, ses dosyası ya da canlı mikrofon akışından çıkarılan ses etiketlerini AST tabanlı bir modelle analiz eden, sonuçları görsel ve metinsel olarak sunan bir web uygulamasıdır.

---

## İçindekiler

- [Özellikler](#özellikler)  
- [Kurulum](#kurulum)  
- [Kullanım](#kullanım)  
  - [API](#api)  
  - [Arayüz](#arayüz)  
- [Yapı](#yapı)  
- [Logger](#logger)  
- [Testler](#testler)  
- [Docker ile Çalıştırma](#docker-ile-çalıştırma)  
- [Katkıda Bulunma](#katkıda-bulunma)  
- [Lisans](#lisans)  

---

## Özellikler

- 🗂️ **Ses Kaydet/Yükle**  
- 🔎 **3 saniyelik parçalar** halinde analiz  
- 📝 **Metin özet**: “Kayıtta ağırlıklı olarak X, arkada Y…”  
- 📊 **Grafikler**: Enerji, Spektral Merkez, Top-3 Skorlar   
- ☁️ **Kolay dağıtım**: FastAPI + Gradio  
- 📦 **Docker desteği**  

---


## Kurulum

1. Depoyu klonlayın:  
   ```bash
   git clone https://github.com/senin-kullanici-adin/AudioSense.git
   cd AudioSense

## Kullanım

### API
uvicorn backend:app --reload
http://127.0.0.1:8000/analyze

### Arayüz
python/python3 frontend.py

---

## Yapı
*backend.py* → FastAPI sunucusu, AST modeli ile sınıflandırma

*frontend.py* → Gradio blok arayüzü, grafik üretimleri

*logger.py* → Basit dosya tabanlı loglam

## Testler
Şu anda manuel test yürütülüyor.

Yakında pytest ile otomasyon eklenecek.

## Docker ile Çalıştırma

docker build -t audiosense .
docker run -p 8000:8000 audiosense

## Lisans

MIT © Taha Cetmili