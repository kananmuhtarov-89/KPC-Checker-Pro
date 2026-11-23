"""Grid-aware OCR: KPC columns only; dates never submitted to OCR."""
from io import BytesIO
from collections import Counter
import re
import cv2
import numpy as np
from PIL import Image
import pytesseract

VALID=re.compile(r'^\d{5,6}$')
SERIAL=re.compile(r'^0*\d{4,5}$')
DATE=re.compile(r'\d{1,2}\s*[./-]\s*\d{1,2}\s*[./-]\s*\d{2,4}')

def _groups(indices,gap=3):
    groups=[]
    for v in indices:
        v=int(v)
        if not groups or v-groups[-1][-1]>gap:groups.append([v])
        else:groups[-1].append(v)
    return [int(np.median(g)) for g in groups]

def _grid(a):
    h,w=a.shape
    b=(a<230).astype('uint8')*255
    vertical=cv2.morphologyEx(b,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_RECT,(1,max(8,h//5))))
    horizontal=cv2.morphologyEx(b,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_RECT,(max(20,w//18),1)))
    xs=_groups(np.where(np.count_nonzero(vertical,axis=0)>h*.38)[0],3)
    ys=_groups(np.where(np.count_nonzero(horizontal,axis=1)>w*.18)[0],4)
    # Keep genuine grid boundaries, discard close text-stroke artifacts.
    if len(xs)<5 or (len(xs)-1)%2 or len(ys)<4:return None
    if xs[-1]-xs[0]<w*.80:return None
    if min(np.diff(xs))<max(9,w*.035):return None
    if min(np.diff(ys))<max(7,h*.035):return None
    if (len(xs)-1)//2>24:return None
    return xs,ys

def _read_cell(a):
    if a.size==0:return None,'empty'
    if (a<180).mean()<.01:return None,'blank'
    scale=max(3,min(7,int(135/max(1,a.shape[0]))))
    z=cv2.resize(a,None,fx=scale,fy=scale,interpolation=cv2.INTER_CUBIC)
    variants=[z,cv2.threshold(z,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]]
    votes=[];raw=[]
    for v in variants:
        for psm in (7,13):
            t=pytesseract.image_to_string(v,config=f'--oem 3 --psm {psm} -c tessedit_char_whitelist=0123456789').strip().replace(' ','')
            raw.append(t)
            if VALID.fullmatch(t) and len(t.lstrip('0'))<=5:votes.append(t.lstrip('0').zfill(5))
    if not votes:return None,'unreadable '+repr(raw)
    best,count=Counter(votes).most_common(1)[0]
    if count<3 or count<=len(votes)-count:return None,'conflict '+repr(raw)
    return best,None

def extract_image(image_data:bytes):
    im=Image.open(BytesIO(image_data)).convert('RGB')
    a=np.array(im.convert('L'))
    grid=_grid(a)
    if grid is None:
        return dict(text='',numbers=[],columns=[],method='Grid not reliably detected',warnings=['Cədvəl sərhədləri aşkarlanmadı; təsdiqlənməmiş rəqəm qaytarılmadı'],expected=None,original_size=im.size,review_required=True)
    xs,ys=grid; pairs=(len(xs)-1)//2
    cols=[];numbers=[];warnings=[];blank=0
    for j in range(pairs):
        values=[]
        for r in range(1,len(ys)-1):
            x1,x2=xs[2*j],xs[2*j+1];y1,y2=ys[r],ys[r+1]
            dx=max(2,round((x2-x1)*.045));dy=max(2,round((y2-y1)*.10))
            code,err=_read_cell(a[y1+dy:y2-dy,x1+dx:x2-dx])
            if code:values.append(code)
            elif err=='blank':blank+=1
            else:warnings.append(f'KPC sütunu {j+1}, sətir {r}: {err}')
        cols.append({'values':values,'raw':'\n'.join(values)});numbers.extend(values)
    return dict(text='\n'.join(numbers),numbers=numbers,columns=cols,method=f'{pairs} KPC sütunu, xana OCR',warnings=warnings,expected=pairs*(len(ys)-2),original_size=im.size,review_required=True,inspected_cells=pairs*(len(ys)-2),blank_cells=blank)
