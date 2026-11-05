"""KPC Checker Pro V9.2 — 2/3 lists, multiple files per list, OCR confirmations."""
from __future__ import annotations
import hashlib
import io
import re
from collections import Counter

import pandas as pd
import streamlit as st
from kpc_core import parse_text, compare

st.set_page_config(page_title='KPC Checker Pro V9.2', page_icon='🔎', layout='wide')
st.title('🔎 KPC Checker Pro V9.2')
st.caption('KPC V6.2 · A/B/C-dən istənilən ikisi və ya üçü · Hər siyahıya çoxsaylı şəkil / TXT / CSV / Excel')
st.info('Hər siyahı üçün **Mətn** və ya **Fayllar** seç. Fayllar rejimində bir neçə şəkil və ya başqa fayl yükləyə bilərsən. PDF qəbul edilmir.')

with st.sidebar:
    st.header('Yoxlama ayarları')
    check_no = st.number_input('Yoxlama №', min_value=1, value=435, step=1)
    st.caption('Yoxlama nömrəsi avtomatik artırılmır: təkrar yoxlamada nömrəni dəyişmə.')
    st.warning('MƏXFİLİK: Public Streamlit Cloud-a göndərilən şəkillər serverdə emal olunur. Yalnız şəxsi məlumatlardan təmizlənmiş KPC cədvəli şəkillərini yüklə.')


def spreadsheet_text(blob: bytes, filename: str, label: str) -> str:
    """Read chosen column from chosen worksheet; each file has its own widgets."""
    try:
        if filename.lower().endswith('.xlsx'):
            workbook = pd.ExcelFile(io.BytesIO(blob))
            sheet = st.selectbox(f'{label}: Excel vərəqi', workbook.sheet_names, key=f'{label}_sheet')
            df = pd.read_excel(io.BytesIO(blob), sheet_name=sheet, dtype=str, header=None).fillna('')
        else:
            try:
                df = pd.read_csv(io.BytesIO(blob), dtype=str, header=None, sep=None, engine='python').fillna('')
            except Exception:
                df = pd.read_csv(io.BytesIO(blob), dtype=str, header=None).fillna('')
        if df.empty or len(df.columns) == 0:
            st.error(f'{label}: faylda məlumat tapılmadı.')
            return ''
        st.dataframe(df.head(8), hide_index=True, use_container_width=True)
        idx = st.selectbox(f'{label}: KPC sütunu', list(range(len(df.columns))), format_func=lambda i: f'Sütun {i + 1}', key=f'{label}_col')
        return '\n'.join(str(v) for v in df.iloc[:, idx].tolist() if str(v).strip())
    except Exception as exc:
        st.error(f'{label}: cədvəl oxunmadı: {type(exc).__name__}: {exc}')
        return ''


def image_text(data: bytes, label: str, identifier: str) -> tuple[str, bool]:
    """One independent review/confirmation for each uploaded image."""
    state_hash = f'{identifier}_hash'
    edit_key = f'{identifier}_edit'
    info_key = f'{identifier}_info'
    confirmed_key = f'{identifier}_confirmed'
    digest = hashlib.sha256(data).hexdigest()
    if st.session_state.get(state_hash) != digest:
        st.session_state[state_hash] = digest
        st.session_state[edit_key] = ''
        st.session_state[info_key] = 'Oxuma hələ başladılmayıb.'
        st.session_state[confirmed_key] = False
    st.image(data, caption=label, use_container_width=True)
    retry = st.button(f'🔄 {label}: OCR-ni yenidən oxu', key=f'{identifier}_retry')
    # Initial OCR tries once per unique uploaded file; retry is explicit.
    done_key = f'{identifier}_done'
    if retry or st.session_state.get(done_key) != digest:
        st.session_state[confirmed_key] = False
        try:
            import shutil
            if not shutil.which('tesseract'):
                raise RuntimeError('Tesseract tapılmadı; Streamlit Cloud üçün packages.txt yoxlanmalıdır.')
            from ocr_engine import extract_image
            with st.spinner(f'{label}: KPC sütunları oxunur...'):
                output = extract_image(data)
            st.session_state[edit_key] = output['text']
            st.session_state[info_key] = f"{len(output['numbers'])} KPC namizədi · {output['method']}"
        except Exception as exc:
            st.session_state[edit_key] = ''
            st.session_state[info_key] = f'OCR XƏTASI: {type(exc).__name__}: {exc}'
        finally:
            st.session_state[done_key] = digest
    info = st.session_state.get(info_key, '')
    if info.startswith('OCR XƏTASI'):
        st.error(info)
    elif st.session_state.get(edit_key, '').strip():
        st.success('OCR: ' + info)
    else:
        st.warning('OCR nəticəsi boşdur. Təkrar oxu və ya nömrələri əl ilə daxil et.')
    st.caption('Yalnız bu şəklin KPC nömrələrini saxla; tarixləri sil. Şəkildəki bütün nömrələri orijinal ilə tutuşdur.')
    edited = st.text_area(f'{label}: KPC nəticəsi (redaktə oluna bilər)', height=135, key=edit_key)
    # Editing invalidates earlier confirmation (important for reliable review).
    validated_key = f'{identifier}_confirmed_text'
    current_fingerprint = hashlib.sha256(edited.encode('utf-8')).hexdigest()
    if st.session_state.get(validated_key) != current_fingerprint:
        st.session_state[confirmed_key] = False
    checked = st.checkbox(f'{label}: bütün KPC-ləri yoxladım, təsdiqləyirəm', key=confirmed_key)
    if checked:
        st.session_state[validated_key] = current_fingerprint
    return edited, bool(checked and edited.strip())


def source(name: str):
    st.subheader(f'{name} siyahısı')
    mode = st.radio(f'{name} daxil etmə üsulu', ['Mətn', 'Fayllar'], horizontal=True, key=f'{name}_mode')
    if mode == 'Mətn':
        raw = st.text_area(f'{name} nömrələri', height=165, key=f'{name}_raw', placeholder='KPC039617, 39618, 039619 ...')
        return raw, bool(raw.strip()), bool(raw.strip()), 0
    uploads = st.file_uploader(f'{name}: bir və ya bir neçə fayl seç', type=['png','jpg','jpeg','webp','txt','csv','xlsx'], accept_multiple_files=True, key=f'{name}_uploads')
    if not uploads:
        return '', False, False, 0
    texts = []
    all_validated = True
    total_images = 0
    # Sorted only for stable interface identities; loaded file order does not matter for comparison.
    for i, file in enumerate(uploads, 1):
        data = file.getvalue()
        suffix = file.name.rsplit('.', 1)[-1].lower()
        identity = hashlib.sha256((name + file.name).encode('utf-8') + data).hexdigest()[:16]
        key = f'{name}_{identity}'
        label = f'{name} · {i}. {file.name}'
        with st.expander(f'📄 {label}', expanded=suffix in ('png','jpg','jpeg','webp')):
            if suffix in ('png', 'jpg', 'jpeg', 'webp'):
                total_images += 1
                content, validated = image_text(data, label, key)
                all_validated &= validated
            elif suffix in ('csv','xlsx'):
                content = spreadsheet_text(data, file.name, key)
                validated = bool(content.strip())
                all_validated &= validated
            else:
                try:
                    content = data.decode('utf-8-sig')
                except UnicodeDecodeError:
                    content = data.decode('cp1251', errors='replace')
                validated = bool(content.strip())
                all_validated &= validated
                st.caption(f'{len(content)} simvol oxundu.')
            if content.strip():
                texts.append(content.strip())
    combined = '\n'.join(texts)
    count = len(parse_text(name, combined).codes) if combined else 0
    st.caption(f'Birləşdirilmiş {name}: {len(uploads)} fayl · {total_images} şəkil · {count} KPC namizədi. Təkrarlar silinmir.')
    if total_images:
        st.warning(f'{name}: bütün {total_images} şəklin nəticəsini ayrıca təsdiqlə. Təsdiqsiz yekun nəticə verilmir.')
    return combined, all_validated and bool(combined.strip()), True, len(uploads)


columns = st.columns(3)
entries = {}
for column, name in zip(columns, ('A','B','C')):
    with column:
        entries[name] = source(name)

st.divider()
if st.button('🔍 3 mərhələli müqayisəni başlat', type='primary', use_container_width=True):
    # A file selection with unreadable content must not be silently omitted.
    chosen = {name: entry for name, entry in entries.items() if entry[2]}
    if len(chosen) < 2:
        st.error('Ən azı iki siyahı doldurulmalıdır.')
        st.stop()
    if any(not entry[1] for entry in chosen.values()):
        st.error('Doldurulmuş siyahılardan biri boş və ya OCR təsdiqsizdir. Yoxlama dayandırıldı.')
        st.stop()
    parsed = {name: parse_text(name, entry[0]) for name, entry in chosen.items()}
    outcome = compare(parsed)
    if outcome['match']:
        st.success(f"№{check_no} — {' = '.join(outcome['names'])} — Uyğun ✅")
    else:
        st.error(f'№{check_no} — Fərq var ❌')
    stats = st.columns(len(outcome['names']) + 1)
    for i, name in enumerate(outcome['names']):
        stats[i].metric(f'{name} sayı', outcome['sizes'][name])
    stats[-1].metric('Fərqli KPC kodları', len(outcome['differences']))
    st.subheader('3 müstəqil yoxlama')
    for check, ok in outcome['checks'].items():
        st.write(('✅' if ok else '❌') + ' ' + check.replace('_', ' '))
    for name, invalid in outcome['invalid'].items():
        if invalid:
            st.error(f"{name} format xətaları: {', '.join(invalid)}")
    if outcome['differences']:
        st.subheader('Fərqlər · hər siyahıda neçə dəfə')
        st.dataframe(pd.DataFrame(outcome['differences']), hide_index=True, use_container_width=True)
    else:
        st.write('Fərqli nömrə yoxdur.')
    st.subheader('Təkrarlar')
    has_duplicates = False
    for name, duplicates in outcome['duplicates'].items():
        if duplicates:
            has_duplicates = True
            st.write(f"**{name}:** " + ', '.join(f'{k} ×{v}' for k, v in duplicates.items()))
    if not has_duplicates:
        st.write('Təkrar nömrə yoxdur.')
    lines = [f"№{check_no} — {'Uyğun ✅' if outcome['match'] else 'Fərq var ❌'}", ' / '.join(f"{n}: {outcome['sizes'][n]}" for n in outcome['names'])]
    lines.extend(f"{n}: {'OK' if passed else 'FƏRQ'}" for n, passed in outcome['checks'].items())
    lines.extend(f"{item['KPC']}: " + ', '.join(f'{n}={item[n]}' for n in outcome['names']) for item in outcome['differences'])
    for name, invalid in outcome['invalid'].items():
        if invalid:
            lines.append(f"{name} format: {', '.join(invalid)}")
    for name, duplicate in outcome['duplicates'].items():
        if duplicate:
            lines.append(f"{name} təkrar: " + ', '.join(f'{c} ×{v}' for c, v in duplicate.items()))
    st.download_button('📄 TXT hesabat', '\n'.join(lines), file_name=f'KPC_{check_no}.txt', mime='text/plain')
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        pd.DataFrame(outcome['differences'], columns=['KPC'] + outcome['names']).to_excel(writer, index=False, sheet_name='Ferqler')
        pd.DataFrame([{'Siyahi': n, 'Say': outcome['sizes'][n]} for n in outcome['names']]).to_excel(writer, index=False, sheet_name='Saylar')
    st.download_button('📊 Excel hesabat', buffer.getvalue(), file_name=f'KPC_{check_no}.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

st.caption('OCR heç vaxt qəti mənbə sayılmır: şəkillər ayrı-ayrı təsdiqlənməlidir. Şəxsi məlumatları public Streamlit Cloud-a yükləmə.')
