"""OCR helper for *cropped KPC tables*. Output is provisional, NEVER trusted automatically.

For standard 3x (KPC, Tarix) tables, OCR the three KPC columns only.
Date fields are not input to the matching algorithm.
"""
from __future__ import annotations
from io import BytesIO
import re
import numpy as np
import cv2
from PIL import Image, ImageOps, ImageEnhance
import pytesseract


def _candidate_lines(text: str) -> list[str]:
    vals = []
    for line in text.splitlines():
        s = line.strip().replace(' ', '')
        s = s.replace('O', '0').replace('o','0') if re.fullmatch(r'[0-9Oo ]{4,8}', s) else s
        # Don't extract numbers out of headings or dates; require standalone numeric row.
        if re.fullmatch(r'0*\d{4,5}', s) and len(s.lstrip('0')) <= 5:
            vals.append(s)
    return vals


def _column_bounds(im: Image.Image):
    a = np.array(ImageOps.grayscale(im))
    binary = cv2.threshold(a,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]
    h,w = binary.shape
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,max(15,h//3)))
    vertical = cv2.morphologyEx(binary,cv2.MORPH_OPEN,kernel)
    strength = (vertical > 0).sum(axis=0)
    cand = np.where(strength > h*.24)[0]
    clusters = []
    for x in cand:
        if not clusters or x-clusters[-1][-1] > 6:
            clusters.append([int(x)])
        else:
            clusters[-1].append(int(x))
    lines=[round(sum(c)/len(c)) for c in clusters]
    # 6 columns + outer boundaries => 7 vertical dividers
    if len(lines)>=7:
        # Choose consecutive boundaries with roughly coherent table span.
        for i in range(len(lines)-6):
            batch=lines[i:i+7]
            widths=np.diff(batch)
            if min(widths)>w*.055 and max(widths)<w*.26 and batch[-1]-batch[0]>w*.65:
                return [(batch[j]+3,batch[j+1]-3) for j in (0,2,4)],'cədvəl sütunları'
    # Fallback: screenshot already cropped to table; require manual checking.
    return [(int(w*i/6)+4,int(w*(i+1)/6)-4) for i in (0,2,4)],'təxmini 3 KPC sütunu'


def extract_image(image_data: bytes):
    image=Image.open(BytesIO(image_data)).convert('RGB')
    if image.width<1100:
        scale=min(3.0,1100/image.width)
        image=image.resize((int(image.width*scale),int(image.height*scale)))
    bounds, method = _column_bounds(image)
    columns=[]
    for x1,x2 in bounds:
        crop=ImageOps.grayscale(image.crop((max(0,x1),0,min(image.width,x2),image.height)))
        crop=ImageEnhance.Contrast(crop).enhance(1.7)
        # Enlarged grayscale for small serial numbers
        crop=crop.resize((crop.width*2,crop.height*2))
        variants=[crop, ImageOps.autocontrast(crop)]
        options=[]
        for var in variants:
            for psm in (6,11):
                raw=pytesseract.image_to_string(var, lang='eng',config=f'--oem 3 --psm {psm} -c tessedit_char_whitelist=0123456789')
                options.append((_candidate_lines(raw),raw))
        best=max(options,key=lambda t:(len(t[0]),sum(len(v) in (5,6) for v in t[0])))
        columns.append({'values':best[0],'raw':best[1]})
    values=[v for col in columns for v in col['values']]
    return {'text':'\n'.join(values),'numbers':values,'method':method,'columns':columns}
