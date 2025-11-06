import io
import datetime
import os
from PyPDF2 import PdfReader, PdfWriter
from endesive import pdf
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Cấu hình
THU_MUC = os.getcwd()
TEN_PDF_GOC = os.path.join(THU_MUC, 'DUY.pdf')
TEN_PFX = os.path.join(THU_MUC, 'cert.pfx')
MAT_KHAU_PFX = b'1234'

# Đọc file gốc
with open(TEN_PDF_GOC, 'rb') as f:
    orig_pdf_bytes = f.read()

reader = PdfReader(io.BytesIO(orig_pdf_bytes))
print("Số trang PDF gốc:", len(reader.pages))

# Thông tin hiển thị chữ ký
dct = {
    'sigflags': 3,
    'sigflagsft': 132,
    # user-visible page index (0-based). For page 4 set to 3
    'page': 3,
    'location': 'Thái Nguyên',
    'contact': '0385289203',
    'signingdate': datetime.datetime.now().strftime("D:%Y%m%d%H%M%S+07'00'"),
    'reason': 'Nộp bài tập',
    'name': 'Nguyễn Khánh Duy',
}

# Load PFX
p12_data = open(TEN_PFX, 'rb').read()
privkey_obj, cert_obj, add_cert_objs = load_key_and_certificates(p12_data, MAT_KHAU_PFX)
if privkey_obj is None or cert_obj is None:
    raise SystemExit("Không load được private key hoặc certificate từ cert.pfx. Kiểm tra mật khẩu.")

othercerts = add_cert_objs if add_cert_objs else []

# Xác định trang mục tiêu (0-based; 3 tương ứng trang 4) và kích thước trang thực tế
target_page = dct.get('page', 0)
if target_page < 0:
    target_page = 0
if target_page >= len(reader.pages):
    target_page = max(0, len(reader.pages) - 1)

page_obj = reader.pages[target_page]
mb = page_obj.mediabox
try:
    page_width = float(mb.width)
    page_height = float(mb.height)
except Exception:
    # fallback A4 nếu không đọc được kích thước
    page_width, page_height = A4

# Tạo overlay (ảnh chữ ký + thời gian ở trên + tên dưới) và ghép lên trang gốc trước khi ký
img_path = os.path.join(THU_MUC, 'anh.png')
sign_time_display = datetime.datetime.now().strftime("Ngày ký: %Y-%m-%d %H:%M")
sign_name_display = dct.get('name')

# Vị trí: góc phải dưới
margin_right = 20 * mm
margin_bottom = 20 * mm
img_w = 60 * mm
img_h = 30 * mm
img_x = page_width - margin_right - img_w
img_y = margin_bottom
# Try to register Times New Roman (Windows). Nếu không tìm thấy, dùng Times-Roman
font_name = 'TimesNewRoman'
font_registered = False
win_fonts = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')
candidates = [
    os.path.join(win_fonts, 'times.ttf'),
    os.path.join(win_fonts, 'Times New Roman.ttf'),
    os.path.join(win_fonts, 'times new roman.ttf'),
    os.path.join(win_fonts, 'timesbd.ttf'),
    os.path.join(win_fonts, 'Times.ttf'),
]
for p in candidates:
    if os.path.exists(p):
        try:
            pdfmetrics.registerFont(TTFont(font_name, p))
            font_registered = True
            break
        except Exception:
            font_registered = False
if not font_registered:
    font_name = 'Times-Roman'

# Prepare overlay canvas
from reportlab.lib.utils import ImageReader
overlay_buf = io.BytesIO()
oc = canvas.Canvas(overlay_buf, pagesize=(page_width, page_height))
# Vẽ thời gian ký và SDT hạ thấp xuống để tránh đè lên nội dung gốc
# Có thể chỉnh nhanh hai thông số dưới đây nếu cần dịch vị trí:
DATE_DROP_MM = 2  # hạ xuống so với mép trên ảnh (mm)
PHONE_GAP_MM = 6  # khoảng cách từ dòng ngày ký xuống dòng SDT (mm)
oc.setFont(font_name, 9)
date_y = img_y + img_h - DATE_DROP_MM * mm
oc.drawCentredString(img_x + img_w/2, date_y, sign_time_display)
oc.setFont(font_name, 9)
phone_y = date_y - PHONE_GAP_MM * mm
oc.drawCentredString(img_x + img_w/2, phone_y, f"SDT: {dct.get('contact')}")
# Vẽ ảnh chữ ký, giữ transparency nếu có
if os.path.exists(img_path):
    try:
        img_reader = ImageReader(img_path)
        oc.drawImage(img_reader, img_x, img_y, width=img_w, height=img_h, mask='auto')
    except Exception as e:
        print("Không thể chèn ảnh chữ ký bằng ImageReader:", e)
else:
    print("Ảnh chữ ký không tìm thấy:", img_path)
# Vẽ tên người ký phía dưới ảnh (căn giữa)
oc.setFont(font_name, 10)
oc.drawCentredString(img_x + img_w/2, img_y - 6*mm, sign_name_display)
oc.save()
overlay_buf.seek(0)

# Ghép overlay lên trang mục tiêu
overlay_pdf = PdfReader(overlay_buf)
writer = PdfWriter()
for i, page in enumerate(reader.pages):
    if i == target_page:
        page.merge_page(overlay_pdf.pages[0])
    writer.add_page(page)

new_pdf_buf = io.BytesIO()
writer.write(new_pdf_buf)
new_pdf_bytes = new_pdf_buf.getvalue()

# Dùng PDF đã ghép overlay làm dữ liệu để ký
datau = new_pdf_bytes

# Chuẩn bị thông tin ký (ẩn annotation, vì phần hiển thị đã được ghép vào nội dung)
page_count = len(reader.pages)
# Dùng chỉ số trang đã chuẩn hóa cho annotation chữ ký
sigpage = target_page if 0 <= target_page < page_count else max(0, page_count - 1)

udct = {
    'sigpage': sigpage,
    'signaturebox': None,  # invisible signature annotation
    'contact': dct.get('contact'),
    'location': dct.get('location'),
    'signingdate': dct.get('signingdate'),
    'reason': dct.get('reason'),
    'sigflags': dct.get('sigflags', 3),
    'sigflagsft': dct.get('sigflagsft', 132),
    'name': dct.get('name'),
}

# Ký bằng endesive
signed_pdf_append = pdf.cms.sign(datau, udct, privkey_obj, cert_obj, othercerts, algomd='sha256')

TEN_DAU_RA = os.path.join(THU_MUC, 'Duy_da_ky.pdf')
with open(TEN_DAU_RA, 'wb') as f:
    f.write(datau + signed_pdf_append)

print("Đã ký thành công! File:", TEN_DAU_RA)

try:
    test_reader = PdfReader(open(TEN_DAU_RA, 'rb'))
    print("PDF hợp lệ! Số trang:", len(test_reader.pages))
except Exception as e:
    print("PDF không hợp lệ:", e)
