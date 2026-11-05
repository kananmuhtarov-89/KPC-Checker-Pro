"""KPC Checker Pro — text/file inputs, 2/3 list multiset audit."""
from __future__ import annotations
import hashlib
import io
import json
from datetime import datetime
import pandas as pd
import streamlit as st
from kpc_core import parse_text, compare

st.set_page_config(page_title='KPC Checker Pro',page_icon='🔎',layout='wide')
st.title('🔎 KPC Checker Pro')
st.caption('KPC V6.2 · İki və ya üç siyahının dəqiq müqayisəsi · Şəkildən oxunan rəqəmlər mütləq təsdiqlənir')
st.info('A, B və C siyahılarından ən azı ikisini doldur. Hər siyahıda Mətn və ya Fayl seçə bilərsən. PDF qəbul edilmir.')

with st.sidebar:
    st.header('Yoxlama ayarları')
    check_no = st.number_input('Yoxlama №',min_value=1,value=435,step=1)
    st.caption('Nömrə avtomatik artırılmır: təkrar yoxlamanın nömrəsi dəyişməməlidir.')
    st.warning('MƏXFİLİK: Streamlit Community Cloud-a yüklənən məlumatlar serverdə emal olunur. Şəxsi məlumat olan şəkilləri bulud tətbiqinə yükləmə. Şəxsi sənədlər üçün lokal versiyanı istifadə et.')


def load_spreadsheet(file, name):
    body=file.getvalue()
    if file.name.lower().endswith('.xlsx'):
        xls=pd.ExcelFile(io.BytesIO(body))
        sheet=st.selectbox(f'{name}: Excel vərəqi',xls.sheet_names,key=f'{name}_sheet')
        df=pd.read_excel(io.BytesIO(body),sheet_name=sheet,dtype=str,header=None).fillna('')
    else:
        try: df=pd.read_csv(io.BytesIO(body),dtype=str,header=None,sep=None,engine='python').fillna('')
        except Exception as ex:
            st.error(f'{name}: CSV oxunmadı: {ex}')
            return ''
    st.caption('Sütunu seç, tarix və başqa məlumat olan sütunları daxil etmə.')
    st.dataframe(df.head(12),hide_index=True,use_container_width=True)
    idx=st.selectbox(f'{name}: KPC sütunu',list(range(len(df.columns))),format_func=lambda i: f'Sütun {i+1}',key=f'{name}_col')
    return '\n'.join(str(v) for v in df.iloc[:,idx].tolist() if str(v).strip())


def get_source(name):
    st.subheader(f'{name} siyahısı')
    method=st.radio(f'{name} daxil etmə üsulu',['Mətn','Fayl'],horizontal=True,key=f'{name}_method')
    if method=='Mətn':
        text=st.text_area(f'{name} nömrələri',height=185,key=f'{name}_typed',placeholder='KPC039617, 39618, 039619 ...')
        return text, True if text.strip() else False, None
    upload=st.file_uploader(f'{name}: fayl yüklə',type=['txt','csv','xlsx','png','jpg','jpeg','webp'],key=f'{name}_upload')
    if upload is None:
        return '',False,None
    extension=upload.name.rsplit('.',1)[-1].lower()
    if extension=='txt':
        data=upload.getvalue()
        try: return data.decode('utf-8-sig'),True,None
        except UnicodeDecodeError:
            return data.decode('cp1251',errors='replace'),True,None
    if extension in ('csv','xlsx'):
        text=load_spreadsheet(upload,name)
        return text,True,None
    st.image(upload.getvalue(),caption=f'{name}: ilkin şəkil',use_container_width=True)
    filehash=hashlib.sha256(upload.getvalue()).hexdigest()
    state_key=f'{name}_ocr_hash'
    edit_key=f'{name}_ocr_edit'
    info_key=f'{name}_ocr_info'
    confirm_key=f'{name}_ocr_confirm'
    # Yalnız tamamlanmış OCR əməliyyatını yadda saxla.
    # Əvvəlki kod hash-i OCR-dən ƏVVƏL yazırdı: Streamlit rerun
    # emalı kəsəndə növbəti açılışda OCR təkrarlanmırdı.
    if st.session_state.get(state_key)!=filehash:
        st.session_state[edit_key]=''
        st.session_state[confirm_key]=False
        st.session_state[info_key]='Yeni şəkil — OCR hələ başlamayıb.'
    retry=st.button(f'🔄 {name}: OCR-ni yenidən oxu',key=f'{name}_ocr_retry',help='OCR boş qalanda və ya yarımçıq kəsiləndə bas.')
    if retry or st.session_state.get(state_key)!=filehash:
        st.session_state[info_key]='OCR başladıldı...'
        try:
            import shutil as _shutil
            import pytesseract as _pt
            if not _shutil.which('tesseract'):
                raise RuntimeError('Tesseract sistemdə tapılmadı. Streamlit Cloud-da packages.txt içində tesseract-ocr olmalıdır.')
            from ocr_engine import extract_image
            with st.spinner(f'{name}: KPC sütunları oxunur...'):
                result=extract_image(upload.getvalue())
            st.session_state[edit_key]=result['text']
            n=len(result['numbers'])
            st.session_state[info_key]=f"{result['method']} · {n} nömrə namizədi"
            st.session_state[state_key]=filehash  # uğurla bitəndən SONRA
            st.session_state[confirm_key]=False
        except Exception as ex:
            st.session_state[info_key]=f'OCR XƏTASI: {type(ex).__name__}: {ex}'
            st.session_state[state_key]=filehash  # xəta üçün retry düyməsi var
    info=st.session_state.get(info_key,'OCR statusu bilinmir. Yenidən oxu düyməsini bas.')
    if info.startswith('OCR XƏTASI'):
        st.error(info)
    elif st.session_state.get(edit_key,'').strip():
        st.success('OCR: '+info)
    else:
        st.warning('OCR: '+info+' — nəticə boşdur. Yenidən oxu və ya nömrələri əl ilə daxil et.')
    st.warning('OCR səhv oxuya, nömrələri ötürə bilər. Ekrandakı KPC-ləri şəkil ilə sətir-sətir yoxla; çatışmayanları əlavə et. Tarixləri daxil etmə.')
    text=st.text_area(f'{name}: OCR nəticəsi (redaktə oluna bilər)',height=185,key=edit_key)
    confirmed=st.checkbox(f'{name}: şəkildəki BÜTÜN KPC nömrələrini orijinalla tutuşdurdum və təsdiqləyirəm',key=f'{name}_ocr_confirm')
    return text, bool(confirmed), 'ocr'

cols=st.columns(3)
entries={}
for col,name in zip(cols,('A','B','C')):
    with col:
        entries[name]=get_source(name)

st.divider()
if st.button('🔍 3 mərhələli yoxlamanı başlat',type='primary',use_container_width=True):
    present={k:v for k,v in entries.items() if v[0].strip() or v[2]=='ocr'}
    if len(present)<2:
        st.error('Ən azı iki siyahı seçilməli və doldurulmalıdır.')
        st.stop()
    if any(not v[1] for v in present.values()):
        st.error('Şəkil siyahısının bütün nömrələri yoxlanılıb təsdiqlənməyib. Yoxlama bloklandı.')
        st.stop()
    parsed={name:parse_text(name,text) for name,(text,_,_) in present.items()}
    result=compare(parsed)
    if result['match']:
        st.success(f'№{check_no} — '+ ' = '.join(result['names'])+' — Uyğun ✅')
    else:
        st.error(f'№{check_no} — Fərq var ❌')
    metrics=st.columns(len(result['names'])+1)
    for i,name in enumerate(result['names']):
        metrics[i].metric(name+' siyahısı',result['sizes'][name])
    metrics[-1].metric('Fərqli KPC kodları',len(result['differences']))
    st.subheader('3 müstəqil Python yoxlaması')
    for label,ok in result['checks'].items():
        st.write(('✅' if ok else '❌')+' '+label.replace('_',' '))
    if any(result['invalid'].values()):
        st.subheader('Format xətaları')
        for name,codes in result['invalid'].items():
            if codes: st.error(f"{name}: {', '.join(codes)}")
    if result['differences']:
        st.subheader('Fərqlər — hər siyahı üzrə neçə dəfə rast gəlinir')
        st.dataframe(pd.DataFrame(result['differences']),hide_index=True,use_container_width=True)
    else:
        st.write('Fərqli nömrə yoxdur.')
    st.subheader('Təkrarlar')
    duplicate_any=False
    for name,items in result['duplicates'].items():
        if items:
            duplicate_any=True
            st.write(f"**{name}:** "+', '.join(f'{k} ×{v}' for k,v in items.items()))
    if not duplicate_any: st.write('Təkrar nömrə yoxdur.')
    lines=[f"№{check_no} — {'Uyğun ✅' if result['match'] else 'Fərq var ❌'}",' / '.join(f"{n}: {result['sizes'][n]}" for n in result['names'])]
    lines.extend(f"{n}: {'OK' if v else 'FƏRQ'}" for n,v in result['checks'].items())
    lines.extend(f"{d['KPC']}: "+', '.join(f'{n}={d[n]}' for n in result['names']) for d in result['differences'])
    for name,items in result['invalid'].items():
        if items: lines.append(f"{name} format xətası: {', '.join(items)}")
    for name,items in result['duplicates'].items():
        if items: lines.append(f"{name} təkrarları: "+', '.join(f'{k} x{v}' for k,v in items.items()))
    st.download_button('📄 TXT hesabatı yüklə','\n'.join(lines),file_name=f'KPC_Yoxlama_{check_no}.txt',mime='text/plain')
    if result['differences']:
        buf=io.BytesIO()
        with pd.ExcelWriter(buf,engine='xlsxwriter') as writer:
            pd.DataFrame(result['differences']).to_excel(writer,index=False,sheet_name='Ferqler')
        st.download_button('📊 Fərqlər Excel',buf.getvalue(),file_name=f'KPC_Ferqler_{check_no}.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

st.caption('Yoxlama yalnız istifadəçinin daxil etdiyi/təsdiqlədiyi nömrələr üzərində aparılır. OCR nəticələri təsdiq edilənədək etibarlı sayılmır.')
