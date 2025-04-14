# 📚 Auto Zotero Importer

Ứng dụng giúp bạn tự động quét thư mục chứa file PDF và đưa toàn bộ vào thư viện Zotero thông qua API.  
Không cần dùng terminal, chỉ cần nhập thông tin cấu hình và chạy `.exe`.

---

# 🚀 Tính năng

- Giao diện hiện đại, thân thiện (CustomTkinter)
- Quét thư mục và phân loại theo cấu trúc thư mục con
- Tự động tạo collections trong Zotero
- Kết nối Zotero qua API key riêng
- Không cần mở terminal khi chạy
- Dễ build thành `.exe`, tiện phân phối

---

# 📦 Cài đặt & sử dụng

### 1. Tải project

Tải thẳng file .exe từ release version hoặc dùng lệnh sau:

```bash
git clone https://github.com/letrinhannd/auto-zotero-importer.git
```

### 2. Tạo file cấu hình Zotero

sửa lại thông tin trong **`API and username.txt`** với nội dung như sau:

```
library_id=library_id_của bạn 
api_key=zotero_api_key_của_bạn
```

**Ví dụ:**

```
library_id=16154628 
api_key=7b4vzNM3oXMgOMXV7KfmQWnm
```

### 3. Cài thư viện cần thiết (nếu chưa)

```
pip install -r requirements.txt
```

### 4. Chạy thử ứng dụng từ mã nguồn

```
python app/main.py
```

### 5.  Build `.exe` để chạy không cần Python

Bước 1: Cài PyInstaller (nếu chưa có)

```
pip install pyinstaller
```

Bước 2: Chạy script build

```
./build_exe.bat
```

Bước 3: Vào thư mục `dist/` và chạy file `.exe`:

```
dist/AutoZoteroImporter.exe
```

### 6. Lấy API key từ Zotero

Bước  1: Vào trang https://www.zotero.org/settings/security, kéo xuống copy user ID ở chỗ bôi đỏ rồi thay vào file .txt 

<img src="https://i.imgur.com/pKZzbM2.png" width="600">
Bước 2: bấm "Create new private key" để tạo API key. 

Bước 3: Chọn các mục như hình, bấm save key, copy và thay vào file .txt username và API.

<img src="https://i.imgur.com/SNMSZ16.png" width="600">

### 7. Chạy chương trình sau khi đã cài đặt

<img src="https://i.imgur.com/SsUncAA.png" width="600">

Bước 1: bấm duyệt và chọn thư mục gốc chứa các thư mục nhỏ gồm các file pdf khác nhau. 

Bước 2: Bấm bắt đầu và đợi tool chạy và tạo các subcollection trong Zotero theo cấu trúc của thư mục gốc. Trong các thư mục sẽ là các link đến các pdf file bên ngoài.

[!] Update: Mỗi lần muốn cập nhật file mới chỉ cần chạy lại tool từ đầu. Tool sẽ tự động ghi đè lên, không bị lặp.


# 📁 Cấu trúc thư mục

```
auto-zotero-importer/
├── app/
│   └── main.py               # Code chính
├── assets/
│   └── icon.ico              # Icon ứng dụng
├── API and username.txt      # File cấu hình Zotero
├── build_exe.bat             # Script build .exe
├── requirements.txt
├── README.md
└── dist/
    └── AutoZoteroImporter.exe  # File .exe sau khi build
```

# ☕ Góp ý & hỗ trợ

Email: github.unmoving893@passinbox.com

