# logger.py
import logging
import sys

# Logger örneğini al / oluştur
info = logging.getLogger("AudioSense")
info.setLevel(logging.INFO)  # INFO ve üzeri seviyeleri görür

# Eğer zaten handler eklenmemişse bir tane ekle
if not info.handlers:
    # Konsola yazdıran handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    # Mesaj formatı: 2025-05-03 12:34:56 INFO: mesajınız
    fmt = "%(asctime)s %(levelname)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    console_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
    info.addHandler(console_handler)

def log(message: str) -> None:
    """
    Basitçe INFO seviyesinde konsola yazdırır.
    Dosyaya yazma veya başka bir işlev yoktur.
    """
    info.info(message)
