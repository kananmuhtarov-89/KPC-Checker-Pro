"""KPC Checker Pro — Streamlit application for V6.1 rules (A/B/C)."""
from __future__ import annotations
from datetime import datetime
from io import BytesIO
import hashlib
import re

import pandas as pd
import streamlit as st
from kpc_core import parse_text, compare
from ocr_engine import read_image

st.set_page_config(page_title='KPC Checker Pro', page_icon='🔎', layout='wide')
st.markdown('''<style>
.block-container {padding-top: 1.5rem; max-width: 1280px;}
h1 {letter-spacing: -.035em;}
div[data-testid="stMetric"] {padding: 14px 18px; background: #f2f5fa; border-radius: 10px;}
</style>''', unsafe_allow_html=True)

st.title('🔎 KPC Checker Pro')
st.caption('V7.0 interfeys · V6.1 müqayisə qaydaları · A / B / C · 3 müstəqil nəzarət')
st.info('**Təhlükəsizlik qaydası:** Şəkildəki OCR nəticəsi təsdiqlənmədən yekun yoxlama aparılmır. '
        'Streamlit Cloud-a yüklənən fayllar bulud serverində emal olunur; məxfi siyahılar üçün lokal işə salın.')

with st.sidebar:
    st.header('⚙️ Yoxlama')
    inspection = st.number_input('Yoxlama nömrəsi', min_value=1, value=435, step=1,
                                 help='Əvvəlki tamamlanan yoxlama №434 idi. Təkrar yoxlama nömrəni artırmır.')
    st.markdown('**Protokol:** V6.1')
    st.markdown('**Standart:** sağdan 5 mövqe, soldakı artıq sıfırlar qəbul edilir; rəqəmlər dəyişdirilmir.')
    st.markdown('**Nəzarət:** say/format + sıralanmış tam müqayisə + Counter.')
    st.divider()
    st.caption('Daxil edilən məlumatlar bu tətbiq tərəfindən daimi fayla və ya bazaya yazılmır. '
               'Brauzer sessiyası və platforma mühiti ayrıca idarə olunur.')


def image_signature(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def get_list_ui(name: str):
    st.subheader(f'{name} siyahısı')
    mode = st.radio(f'{name} daxil etmə üsulu', ['Mətn', 'Fayl'], horizontal=True, key=f'{name}_mode')
    if mode == 'Mətn':
        txt = st.text_area(f'{name} nömrələrini daxil et', height=180,
                           placeholder='KPC039617, 39623, KPC 039694, ...', key=f'{name}_text')
        st.caption('Vergül, boşluq və ya yeni sətirlə ayıra bilərsən.')
        return txt, True

    file = st.file_uploader(f'{name}: Excel, CSV, TXT və ya şəkil seç',
                            type=['xlsx','xlsm','csv','txt','png','jpg','jpeg','webp'],
                            key=f'{name}_upload')
    if file is None:
        return '', False
    extension = file.name.lower().rsplit('.', 1)[-1]
    data = file.getvalue()
    if extension in ('png','jpg','jpeg','webp'):
        st.image(data, caption=f'{name}: ilkin şəkil', use_container_width=True)
        sig = image_signature(data)
        sigkey = f'{name}_ocr_signature'
        if st.session_state.get(sigkey) != sig:
            with st.spinner('Şəkildən mətn oxunur...'):
                try:
                    extracted, _ = read_image(data)
                except Exception as exc:
                    st.error(f'OCR oxuma xətası: {exc}. Tesseract quraşdırılmasını yoxla.')
                    return '', False
            st.session_state[sigkey] = sig
            st.session_state[f'{name}_ocr_edit'] = extracted
            st.session_state[f'{name}_ocr_confirm'] = False
        st.warning('OCR yanılda bilər. Bütün nömrələri şəkillə sətir-sətir yoxla. '
                   'Tarix, başlıq və digər rəqəmləri sil; çatışmayan nömrələri əlavə et.')
        txt = st.text_area(f'{name} — OCR mətni (redaktə oluna bilər)', height=230,
                           key=f'{name}_ocr_edit')
        confirmed = st.checkbox(f'{name}: Şəkildəki bütün nömrələri yoxladım və təsdiqləyirəm',
                                key=f'{name}_ocr_confirm')
        return txt, confirmed

    try:
        if extension in ('xlsx','xlsm'):
            book = pd.ExcelFile(BytesIO(data))
            sheet = st.selectbox(f'{name}: Excel vərəqi', book.sheet_names, key=f'{name}_sheet')
            frame = pd.read_excel(BytesIO(data), sheet_name=sheet, dtype=str, header=None).fillna('')
        elif extension == 'csv':
            frame = pd.read_csv(BytesIO(data), dtype=str, header=None, sep=None,
                                engine='python', keep_default_na=False)
        else:
            try:
                return data.decode('utf-8-sig'), True
            except UnicodeDecodeError:
                return data.decode('cp1251'), True
    except Exception as exc:
        st.error(f'Fayl oxunmadı: {exc}')
        return '', False

    if frame.empty:
        st.error('Faylın seçilmiş vərəqi boşdur.')
        return '', False
    options = list(range(len(frame.columns)))
    choice = st.selectbox(f'{name}: KPC nömrələrinin olduğu sütun', options,
                          format_func=lambda idx: f'Sütun {idx+1} — {str(frame.iloc[0, idx])[:35]}',
                          key=f'{name}_col')
    selected = [str(v).strip() for v in frame.iloc[:, choice] if str(v).strip()]
    st.caption(f'Seçilmiş sütunda {len(selected)} boş olmayan xana tapıldı.')
    with st.expander(f'{name} — oxunan məlumatlara bax'):
        st.dataframe(pd.DataFrame({'Oxunan dəyər': selected}), hide_index=True)
    # Allows human confirmation/correction of unexpected headers or invalid cells.
    signature = image_signature(data + f':{choice}:{extension}:{locals().get("sheet", "")}'.encode())
    if st.session_state.get(f'{name}_tab_signature') != signature:
        st.session_state[f'{name}_tab_signature'] = signature
        st.session_state[f'{name}_tab_edit'] = '\n'.join(selected)
    txt = st.text_area(f'{name}: Seçilmiş sütunu lazım gəlsə düzəlt', height=170,
                       key=f'{name}_tab_edit')
    return txt, True


st.write('A, B və C-nin hər birinə ayrıca mətn daxil edə və ya fayl yükləyə bilərsən.')
cols = st.columns(3)
text_by_list = {}
ready_by_list = {}
for name, col in zip('ABC', cols):
    with col:
        text_by_list[name], ready_by_list[name] = get_list_ui(name)

parsed = {name: parse_text(name, text_by_list[name]) for name in 'ABC'}
st.divider()
st.subheader('📋 İlkin yoxlama')
metric_cols = st.columns(3)
for name, col in zip('ABC', metric_cols):
    with col:
        p = parsed[name]
        st.metric(f'{name} — düzgün formatlı nömrələr', len(p.codes))
        if p.invalid:
            st.error(f'{len(p.invalid)} qəbul edilməyən token: {", ".join(p.invalid[:12])}')
        elif p.codes:
            st.caption('Format yoxlaması: keçdi')
        else:
            st.caption('Siyahı hələ boşdur')

all_sources_ready = all(ready_by_list.values())
all_have_data = all(p.codes and not p.invalid for p in parsed.values())
if not all_sources_ready:
    st.warning('Bütün siyahılar yüklənməli, şəkil olanlar isə ayrıca təsdiqlənməlidir.')
if not all_have_data:
    st.warning('A, B və C-də boş və ya yanlış formatlı siyahı qalmamalıdır.')

run = st.button('🔍 3 mərhələli yoxlamanı başlat', type='primary',
                disabled=not (all_sources_ready and all_have_data), use_container_width=True)

# Invalidate previous result when any input, confirmation, or selection changes.
input_fingerprint = image_signature(('\x1d'.join(text_by_list[k] for k in 'ABC') +
                                    '|' + repr(tuple(ready_by_list[k] for k in 'ABC')) +
                                    '|' + str(inspection)).encode('utf-8'))
if run:
    st.session_state['last_result'] = compare(parsed)
    st.session_state['last_fingerprint'] = input_fingerprint
    st.session_state['last_inspection'] = inspection

if st.session_state.get('last_fingerprint') == input_fingerprint and 'last_result' in st.session_state:
    result = st.session_state['last_result']
    st.divider()
    st.subheader(f'Yekun nəticə — №{inspection}')
    if result['match']:
        st.success(f'№{inspection} — A = B = C — UYĞUN ✅')
    else:
        st.error(f'№{inspection} — FƏRQ VAR ❌')

    st.markdown('**3 müstəqil nəzarətin nəticəsi**')
    checks = result['checks']
    for label, val in [
        ('1. Say və format', checks['count_and_format']),
        ('2. Tam sıralanmış müqayisə', checks['sorted_full_comparison']),
        ('3. Counter çoxluq müqayisəsi', checks['counter_multiset']),
    ]:
        st.write(('✅' if val else '❌') + ' ' + label)

    st.write(f"**A: {result['sizes']['A']} · B: {result['sizes']['B']} · C: {result['sizes']['C']}**")
    if result['differences']:
        st.markdown('**Fərqli KPC-lər — hər siyahıdakı dəqiq təkrarlanma sayı**')
        st.dataframe(pd.DataFrame(result['differences']), hide_index=True, use_container_width=True)
    else:
        st.write('Fərqli nömrə yoxdur.')
    dup_rows = [{'Siyahı': key, 'KPC': code, 'Təkrar sayı': value}
                for key, items in result['duplicates'].items() for code, value in items.items()]
    if dup_rows:
        with st.expander(f'Təkrarlanan nömrələr ({len(dup_rows)} qeyd)'):
            st.dataframe(pd.DataFrame(dup_rows), hide_index=True)
    else:
        st.caption('Təkrar nömrə: 0')

    status = 'UYĞUN ✅' if result['match'] else 'FƏRQ VAR ❌'
    lines = [f'№{inspection} — {status}',
             f"A: {result['sizes']['A']} | B: {result['sizes']['B']} | C: {result['sizes']['C']}",
             f"1. Say/format: {checks['count_and_format']}",
             f"2. Sıralanmış: {checks['sorted_full_comparison']}",
             f"3. Counter: {checks['counter_multiset']}"]
    lines.extend(f"{r['KPC']}: A={r['A']}, B={r['B']}, C={r['C']}" for r in result['differences'])
    txt_report = '\n'.join(lines)

    def excel_report():
        output = BytesIO()
        summary = pd.DataFrame([
            {'Siyahı': name, 'Nömrə sayı': result['sizes'][name],
             'Təkrar nömrə növü': len(result['duplicates'][name])} for name in 'ABC'])
        differences = pd.DataFrame(result['differences'], columns=['KPC','A','B','C'])
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            summary.to_excel(writer, sheet_name='Yekun', index=False)
            differences.to_excel(writer, sheet_name='Ferqler', index=False)
            for key in 'ABC':
                pd.DataFrame({'KPC': parsed[key].codes}).to_excel(writer, sheet_name=f'Siyahi_{key}', index=False)
        return output.getvalue()

    dc1, dc2 = st.columns(2)
    with dc1:
        st.download_button('⬇️ Qısa TXT hesabatı', txt_report.encode('utf-8-sig'),
                           file_name=f'KPC_{inspection}_hesabat.txt', mime='text/plain', use_container_width=True)
    with dc2:
        st.download_button('⬇️ Excel hesabatı', excel_report(),
                           file_name=f'KPC_{inspection}_hesabat.xlsx',
                           mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                           use_container_width=True)
else:
    st.caption('Nəticə yalnız “3 mərhələli yoxlamanı başlat” düyməsi ilə və cari siyahılar üzrə hesablanır.')
