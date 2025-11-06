# Bài tập chữ ký số – Hướng dẫn nhanh

Các file chính:
- `tao_khoa.py`: Tạo cặp khóa, chứng chỉ tự ký và gói `cert.pfx` (mật khẩu 1234).
- `tao_pdf_mau.py`: Tạo file PDF mẫu 4 trang `DUY.pdf` để ký.
- `ky.py`: Ký số lên PDF bằng gói `cert.pfx` (tạo file `Duy_da_ky.pdf`).
- `check_ky.py`: Kiểm tra chữ ký số trong PDF (ghi 8 dòng kết quả vào `nhat_ky_check.txt`).

## Cài môi trường và thư viện

1) Cài Python 3.10+ trên Windows.
2) Cài các thư viện:

```powershell
pip install -r requirements.txt
```

## Tạo khóa và chứng chỉ tự ký

Chạy tạo khóa/cert và gói PFX (pass: 1234):

```powershell
python .\tao_khoa.py
```

Sinh ra các file:
- `private_key.pem`, `public_key.pem`
- `cert.pem`, `cert.cer`
- `cert.pfx` (mật khẩu 1234)

## Tạo PDF mẫu để ký

```powershell
python .\tao_pdf_mau.py
```

Sinh `DUY.pdf` (4 trang). Bạn có thể thay bằng tài liệu của bạn, nhưng `ky.py` đang mặc định dùng `DUY.pdf` ở cùng thư mục.

## Ký số PDF

Đặt (tùy chọn) ảnh chữ ký `anh.png` vào cùng thư mục để in đè lên trang ký. Nếu không có ảnh, script vẫn ký hợp lệ nhưng chỉ thêm chữ hiển thị.

```powershell
python .\ky.py
```

Kết quả: `Duy_da_ky.pdf`

## Kiểm tra chữ ký

```powershell
python .\check_ky.py .\Duy_da_ky.pdf --trust-local-pfx
```

Script sẽ in ra 8 dòng trạng thái và ghi vào `nhat_ky_check.txt`.

Lưu ý: vì dùng chứng chỉ tự ký (không phải CA tin cậy), kiểm tra chuỗi tin cậy có thể KHÔNG HỢP LỆ trừ khi dùng `--trust-local-pfx`.

## Tùy chỉnh

- Đổi mật khẩu PFX: sửa `PFX_PASSWORD` trong `tao_khoa.py` và cập nhật `MAT_KHAU_PFX` trong `ky.py`.
- Đổi trang hiển thị chữ ký: sửa `dct['page']` trong `ky.py` (0-based; 3 tức là trang 4).
- Đổi nội dung hiển thị: cập nhật `dct` trong `ky.py`.