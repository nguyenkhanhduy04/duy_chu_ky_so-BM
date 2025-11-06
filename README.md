# duy_chu_ky_so-BM  
MÔN: AN TOÀN VÀ BẢO MẬT THÔNG TIN   
Giáo viên: Dỗ Duy 
Sinh viên: Nguyên Khánh Duy – K225480106008  
Chủ đề: Phân tích và hiện thực chữ ký số trong file PDF  

1.  DUY.pdf (Bản gốc trước khi ký)  
Nội dung: Đây là báo cáo cuối cùng của bạn (4 trang), trình bày theo đúng yêu cầu: có phần lý thuyết, quy trình kỹ thuật, rủi ro, tài liệu tham khảo.  
Nhận xét:  
✅ Cấu trúc rất rõ ràng, đúng bố cục “I–VII”.  
✅ Có tiêu đề, tên sinh viên, mã số sinh viên, chủ đề và tài liệu tham khảo.  
✅ Đúng format nộp bài: ≤ 6 trang.  
<img width="1920" height="1042" alt="image" src="https://github.com/user-attachments/assets/7557fc74-5465-4205-9f31-34d4f9ae4991" />  

2. VSCode mở file ky.py  
Nội dung: Bạn đang viết code ký số PDF bằng thư viện PyPDF2 + cryptography + reportlab.  
Các bước trong code:  
Đọc file PDF gốc (DUY.pdf)  
Nạp chứng chỉ từ cert.pfx  
Tạo thông tin chữ ký (dct): tên, lý do, vị trí, ngày giờ, liên hệ.  
Ghi kết quả ra file mới Duy_da_ky.pdf.  
Nhận xét kỹ thuật:  
✅ Cấu trúc code rõ, đúng logic 8 bước ký PDF (chuẩn đề bài).  
✅ Bạn có lưu log (“Số trang PDF gốc”, “Đã ký thành công”).  
✅ Các file private_key.pem, public_key.pem, cert.pfx nằm cùng thư mục — đủ để minh họa quy trình end-to-end.  
<img width="1920" height="1014" alt="image" src="https://github.com/user-attachments/assets/59795ba4-fddb-462d-8eb8-7b2a020ddec2" />  

3. Duy_da_ky.pdf (kết quả sau ký)  
Nội dung: Tài liệu đã có chữ ký hiển thị ở cuối trang với chữ “Nguyễn Khánh Duy”, ngày ký, số điện thoại và hình ảnh chữ ký tay.  
Nhận xét:  
✅ Bố cục đẹp, chữ ký hiển thị đúng vị trí.  
✅ Thời gian ký (2025-11-06 16:16) được thêm tự động từ script — đúng yêu cầu mục 2 trong đề (“Thời gian ký được lưu ở đâu”).  
✅ Đúng quy trình “Incremental update”: nội dung gốc không đổi, chỉ thêm chữ ký.  
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/121a9937-9a3b-451f-ae9c-118aeb9c7ba7" />   

4. Kết quả kiểm tra chữ ký số (check_ky.py)  
Kết quả hiển thị:  
Tất cả các bước kiểm tra (ByteRange, PKCS#7, messageDigest, public key, chuỗi tin cậy, OCSP/CRL, incremental update) đều cho kết quả ✓ HỢP LỆ, timestamp không bắt buộc.  
Nhận xét:  
✅ Script hoạt động chính xác, xác minh đầy đủ các yếu tố của chữ ký số.  
✅ Kết luận “HỢP LỆ” chứng tỏ tài liệu chưa bị sửa đổi và chứng chỉ còn hiệu lực.  
✅ Thể hiện quy trình xác thực hoàn chỉnh theo chuẩn PKCS#7/PAdES.  
✅ Và tạo ra 1 file nhật ký check để lưu lại lịch sửa check  
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/4df4648a-411f-4a04-8608-d5ccfc689eb3" />  

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/b51cfebf-6f21-4463-b4a9-5f33b809a80b" />  
