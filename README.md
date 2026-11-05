# KPC Checker Pro

Üç siyahının (A/B/C) müqayisəsi üçün Streamlit tətbiqi. **V6.1 protokolu** saxlanılır; vizual tətbiq versiyası **V7.0**.

## Funksiyalar

- Hər siyahıya mətn, `.txt`, `.csv`, `.xlsx` / `.xlsm`, `.png`, `.jpg`, `.jpeg`, `.webp` daxil etmə
- Excel vərəqi və KPC sütununun seçilməsi
- Şəkillərdən Tesseract OCR ilə ilkin oxuma və **məcburi insan təsdiqi**
- KPC/KPÇ prefiksi və boşluqların silinməsi; solda artıq sıfırların qəbul edilməsi; 5 mövqenin dəqiq uyğunluğu
- 3 nəzarət: **(1) say/format, (2) tam sıralanmış siyahılar, (3) `Counter` ilə təkrarlanma və fərq**
- Uyğunsuz hər kod üçün A/B/C-dəki sayın göstərilməsi
- Excel və TXT hesabatları; yoxlama nömrəsinin əl ilə idarə edilməsi
- Proqram istifadəçi fayllarını diskə/bazaya yazmır; sessiya daxilində emal edir

## Lokal kompüterdə işlətmək

Python 3.10+ və Tesseract OCR qurulur. Windows üçün [Tesseract OCR quraşdırma məlumatı](https://github.com/UB-Mannheim/tesseract/wiki). `tesseract` PATH-də olmalıdır.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Brauzerdə açılan ünvana keç (adətən `http://localhost:8501`). Lokal işə salınanda məlumatlar öz kompüterində emal edilir.

## GitHub-a əlavə etmək

1. GitHub-da yeni, tercihen **private** repository yarat.
2. ZIP-dən çıxarılan **`KPC_Checker_Pro` qovluğunun içindəki faylları** repository-nin kökünə yüklə. `app.py`, `requirements.txt`, `packages.txt`, `kpc_core.py`, `ocr_engine.py` eyni səviyyədə olmalıdır.
3. GitHub-a yüklənmiş fayllara şəxsi KPC siyahıları və real ekran görüntüləri əlavə etmə.

## Streamlit Community Cloud deploy

1. [share.streamlit.io](https://share.streamlit.io/) saytına GitHub hesabı ilə daxil ol.
2. **Create app / Deploy an app** seç; repository və branch seç.
3. **Main file path:** `app.py`.
4. Deploy et. `requirements.txt` Python paketlərini, `packages.txt` isə Linux-da Tesseract OCR-i quraşdıracaq.
5. İlk girişdə 3 siyahını doldur; şəkil yüklənibsə OCR mətni orijinalla tutuşdurub təsdiqlə; sonra **Yoxla**.

**Məxfilik:** Community Cloud serverində fayllar emal olunur. Tətbiqin özündə fayllar diskə yazılmasa da, bunu tam lokal məxfilik zəmanəti kimi qəbul etmə. Həssas məlumat üçün lokal rejimi seç. Buludda public tətbiqə anonim istifadəçilərin girişi ola bilər; giriş nəzarətini ayrıca planlaşdır.

## Qaydalar və məhdudiyyətlər

- `KPC018569`, `KPC 018569`, `18569` → `18569`.
- `00000123` → `00123`. `123456` rədd edilir (6 əhəmiyyətli rəqəm).
- Yalnız 5 mövqenin hamısı uyğun gələndə eyni sayılır. Təxmini düzəltmə, yerdəyişmə yoxdur.
- **OCR zəmanətli deyil:** OCR çıxışında tarix, ad və digər məlumatlar görünə bilər; hamısını əl ilə silib/təsdiq et. Şübhəli nömrənin yoxlanması bitmədən “Uyğun” nəticəsini qəbul etmə.
- Üç yoxlama **eyni giriş mətnindən** istifadə edir; buna görə mənbədəki yanlış OCR rəqəmini avtomatik aşkarlaya bilməz.
- Sütun başlıqları daxil edilmişsə əl ilə silinməlidir; xətalı token nəticəni bloklayır.
- Cari sessiyada yoxlama nömrəsi əl ilə seçilir; persistent tarixçə saxlanılmır.

## Testlər

```bash
pip install pytest
pytest -q
```

## Layihə strukturu

- `app.py` — interfeys, fayl yükləmə, hesabat
- `kpc_core.py` — yoxlama qaydaları, format və `Counter`
- `ocr_engine.py` — OCR oxuma
- `requirements.txt` — Python asılılıqları
- `packages.txt` — Linux üçün Tesseract
- `.streamlit/config.toml` — interfeys ayarları
- `tests/test_core.py` — avtomatik testlər
