# KPC Checker Pro V9.3 — Multi-File OCR

KPC yoxlama protokolu V6.2: siyahılar A/B/C; ən azı **iki siyahı** doldurulmalıdır. Uyğunluq üçün say/format, sıralanmış tam siyahı və `Counter` multiset müqayisəsi aparılır. Hər siyahıda mətn və ya **istənilən sayda fayl** seçilə bilər.

## Nə yenidir?

- A, B, C üçün hər birində `Mətn` və ya `Fayllar` rejimi.
- `Fayllar` rejimində eyni anda bir neçə PNG/JPG/JPEG/WEBP, TXT, CSV, XLSX (qarışıq da olar) yüklə.
- Hər şəkil **ayrıca** OCR olunur, nəticəsi ayrıca redaktə edilir və ayrıca təsdiqlənir.
- Seçilmiş faylların nömrələri birləşdirilir; təkrarlar **silinmir**.
- OCR səhv/yarımçıq oxuyanda `OCR-ni yenidən oxu` düyməsi və redaktə sahəsi var.
- PDF **qəbul edilmir**. Print Screen edərkən **yalnız KPC cədvəlini** kəs.
- Fayl/şəkil təsdiqsiz və ya boşdursa, yekun uyğunluq bloklanır.

## GitHub və Streamlit Community Cloud

1. Bu ZIP-dəki **faylları və gizli `.streamlit` qovluğunu** GitHub repository kökünə yüklə; köhnə `app.py` və digər eyniadlı faylları dəyişdir.
2. `requirements.txt` və `packages.txt` kökdə qalsın (Linux serverdə Tesseract qurulması üçün).
3. Streamlit Community Cloud: branch `main`, **Main file path `app.py`**.
4. Mövcud deploy adətən GitHub commit-ə görə avtomatik yenilənir. Açılmasa tətbiqi reboot et / logları yoxla.

## İstifadə

1. Yoxlama nömrəsini (məs. 435) daxil et.
2. A, B və/və ya C-də `Mətn`/`Fayllar` seç; ən az iki siyahını doldur.
3. `Fayllar` rejimində bir neçə şəkil yükləmək üçün `Browse files` vasitəsilə faylları birlikdə seç və ya sonradan əlavə et.
4. Hər şəklin ayrıca bölməsini aç; OCR-də **bütün** KPC-ləri orijinal şəkillə tutuşdur; çatışmayan/səhv nömrələri düzəlt; sonra həmin şəklin təsdiq qutusunu işarələ.
5. `3 mərhələli müqayisəni başlat` düyməsini bas.
6. Fərqlərə və təkrarlara bax, TXT/Excel çıxart.

**Diqqət:** OCR fərqləri qaçıra bilər. Əl ilə təsdiq real gözlə yoxlama deməkdir, avtomatik zəmanət deyil. Şəkillərin KPC nömrəsi olan **sütunları** sistem tərəfindən oxunur; tarix sütunları OCR mətninə daxil edilməməlidir.

## Məxfilik

Community Cloud-da fayllar serverdə emal edilir. Şəxsi məlumat, müqavilənin məxfi hissələri, şəxsiyyət sənədləri olan şəkilləri yükləmə. Həssas sənədlər üçün eyni kodu **lokal** `streamlit run app.py` ilə işlətmək olar; Tesseract yerli kompüterdə qurulmalıdır.

## Test

```bash
python -m unittest discover -s tests -v
```

## Əsas fayllar

- `app.py` — Streamlit interfeysi və multi-file yükləmə
- `kpc_core.py` — deterministik normallaşdırma və 3 mərhələli müqayisə
- `ocr_engine.py` — şəkil cədvəlində KPC sütunlarından namizədlər
- `requirements.txt`, `packages.txt` — bulud asılılıqları


## V9.3 düzəlişi
Şəkil üzrə OCR təsdiq checkbox-u işarələnən anda artıq öz-özünə sönmür. Mətn redaktə ediləndə təsdiq yenidən tələb olunur.

## V10.0 OCR təhlükəsizlik yenilənməsi
- 6/8 sütunlu KPC/Tarix cədvəlləri üçün ayrıca xana OCR və zəif cədvəl xətləri üçün ehtiyat sütun OCR.
- Tarix sütunları oxunmur, şübhəli/oxunmayan sahələr diaqnostikada göstərilir.
- Ehtiyat OCR də səhv edə bilər: şəkil nəticəsi insan tərəfindən təsdiqlənmədən müqayisəyə buraxılmır.
- Test şəkillərində birinci nümunə 19 namizəd, ikinci 18 namizəd verdi, lakin səhv rəqəmlər də oldu. Bu, avtomatik dəqiqliyin təminatı deyil; diaqnostika və əl ilə tutuşdurma məcburidir.

## V11 təhlükəsizlik qeydi
- 300+ kodun mətn müqayisəsi test olunur. Şəkildən 300 kodun etibarlı çıxarılması görüntünün ölçüsündən və cədvəl quruluşundan asılıdır.
- OCR şübhəli cədvəldə nəticə uydurmur, əllə yoxlama tələb edir.
- 23.11.2026 tarixli iki kiçik ekran şəklində bu konservativ OCR avtomatik nəticə vermədi. Bu, dəqiqlik uğuru deyil; yanlış müsbət nəticələrin qarşısını alma tədbiridir.
- Daha yüksək dəqiqlik üçün gələcək mərhələdə xananın lokalizasiyası və OCR alternativi üzərində işləmək lazımdır.

## V12: problemli 2 şəkil üzrə təsdiqlənmiş OCR
- OCR 4 KPC + 4 tarix sütunlu cədvəli avtomatik aşkarlayır; tarix sütunları oxunmur.
- Orijinal 842×201 və 490×119 ölçülü şəkillər `tests/fixtures/` içindədir.
- Hər iki şəkil üçün 19/19 düzgün KPC (5 rəqəmli normallaşdırılmış) və 1 boş xana testlə təsdiqlənib.
- 300 kodlu mətn müqayisəsi test olunub; 300 kodlu şəkil OCR-si hələ ayrıca real test tələb edir.
- OCR təsdiqi yenə istifadəçinin yoxlamasını tələb edir. Naməlum şablonlarda etibarsız nəticə əvəzinə xəbərdarlıq verilir.
- Lokal test: `python -m pytest -q`.

### V14 (2026-11-23)
- Automatic line-angle detection and deskew before grid OCR.
- Tested on 3-column skewed screenshot: 13/13 serials, 2 empty cells, 0 dates.
- Regression tested on two 4-column screenshots: 19/19 serials each.
- OCR does not silently confirm results; user review remains required.
- 300-entry text comparisons are supported; 300-entry image OCR is not yet empirically verified.
