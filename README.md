# KPC Checker Pro V9.1 — OCR düzəlişi

V9.0 funksiyaları saxlanılıb. OCR işləməsə `OCR-ni yenidən oxu` düyməsi var. OCR statusu/xətası həmişə göstərilir. İlk versiyanın əsas problemi: fayl hash-i OCR tamamlanmadan yazılırdı; emal kəsiləndə nəticə boş qalırdı.

GitHub repository-də əsas faylları ZIP içindən yeniləyin (`app.py` və qalanları). Streamlit Cloud avtomatik yenidən deploy edə bilər; lazım gələrsə Reboot app basın. `packages.txt` içində `tesseract-ocr`, `libgl1` olmalıdır. Məxfi sənədləri Cloud-a yükləməyin.
