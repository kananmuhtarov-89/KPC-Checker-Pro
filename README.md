# KPC Checker Pro V9 — Streamlit Cloud

**KPC V6.2 qaydaları:** A+B, A+C, B+C və ya A+B+C müqayisəsi; sıra önəmsiz; təkrar sayı vacibdir. Bütün 5 rəqəm ayrı-ayrılıqda uyğun olmalıdır. `KPC`, `KPÇ`, boşluqlar və artıq başlanğıc sıfırları nəzərə alınmır. 5-dən çox **əhəmiyyətli** rəqəm qəbul edilmir. 3 müstəqil Python yoxlaması: (1) say+format, (2) sıralanmış tam siyahı, (3) Counter multiset.

## GitHub-a yerləşdirmə

1. ZIP faylını kompüterdə **Extract All** ilə açın.
2. GitHub repository-yə ZIP-i deyil, **içindəki faylları** yerləşdirin. `app.py`, `ocr_engine.py`, `kpc_core.py`, `requirements.txt`, `packages.txt` əsas qovluqda olmalıdır.
3. Streamlit Community Cloud: repository seçin, branch `main`, main file `app.py`, Deploy.
4. Mövcud tətbiqdirsə, GitHub-da köhnə `app.py`, `kpc_core.py`, `ocr_engine.py`, `requirements.txt`, `packages.txt` fayllarını yeni məzmunla əvəz edin; Streamlit yenilənəcək.

## İstifadə

- A, B, C-dən ən az iki siyahını doldurun.
- Hər siyahıda ayrıca **Mətn** və ya **Fayl** seçin. Fayl: PNG, JPG, WEBP, TXT, CSV, XLSX. **PDF yoxdur.**
- Print Screen şəklini yalnız KPC və tarix cədvəlinin olduğu hissədən edin. OCR 3 KPC sütununu oxumağa çalışacaq, tarix sütunları nəzərə alınmır.
- OCR nəticəsini **hər nömrə üzrə** orijinal ilə müqayisə edin. Yanlışları dəyişin, əskikləri əlavə edin və təsdiq qutusunu işarələyin. OCR boş qalırsa, nömrələri əllə həmin xanaya yaza bilərsiniz.
- Yoxlama düyməsinə basın. Nəticə və fərqlər, təkrarlar görünəcək. TXT və fərq olduqda Excel hesabatı mümkündür.
- Yoxlama № əl ilə idarə olunur; təkrar yoxlama nömrəni artırmır.

## Məxfilik — VACİB

Public/private Streamlit Cloud fərq etmədən **yüklənən fayllar Streamlit serverində emal edilir**. Şəxsi məlumatlı sənədləri və ekran görüntülərini təşkilatın icazəsi olmadan Cloud-a yükləməyin. Yalnız KPC cədvəlini ehtiva edən, başqa şəxsi sahələri kəsilmiş screenshot istifadə edin; **KPC seriya nömrələri də kontekstdən asılı olaraq həssas iş məlumatı ola bilər.** Tam məxfi sənədlər üçün lokal Streamlit quraşdırın və `streamlit run app.py` istifadə edin. Proqramda xüsusi xarici OCR API yoxdur; bulud deployment-in özü yenə də üçüncü tərəfdə emaldır.

## Test

`python -m unittest discover -s tests -v`

## OCR qeydləri

Tesseract şəkillərdəki simvolları səhv oxuya, təkrarlaya və ya buraxa bilər. OCR sütunlara görə oxumaq üçün cədvəldəki şaquli xətləri tapır; tapılmasa eninə görə təxmini bölgülərdən istifadə edir. Nəticə **avtomatik təsdiqlənmir**. Screenshot mümkün qədər yalnız cədvəl olsun, aydın və yüksək keyfiyyətli olsun. Qeyri-standart cədvəllər əl ilə yoxlanmalıdır.
