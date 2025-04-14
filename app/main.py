import os
import time
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pyzotero import zotero
import logging

# ========== Đọc file cấu hình ==========
def load_config(file_path):
    config = {}
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if '=' in line:
                    key, val = line.strip().split('=', 1)
                    config[key.strip()] = val.strip()
    except FileNotFoundError:
        raise FileNotFoundError("Không tìm thấy file cấu hình.")
    return config

# ========== Giao diện ==========
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Auto Zotero Importer")
        self.geometry("700x550")
        self.resizable(False, False)

        self.config_file_path = None  # Đường dẫn tới file cấu hình

        self.build_ui()
        self.setup_logging()

    def build_ui(self):
        # Chọn thư mục PDF
        self.label = ctk.CTkLabel(self, text="Chọn thư mục chứa PDF:", font=("Arial", 16))
        self.label.pack(pady=10)

        self.entry = ctk.CTkEntry(self, width=500)
        self.entry.pack(pady=5)

        self.browse_btn = ctk.CTkButton(self, text="Chọn thư mục gốc", command=self.browse_dir)
        self.browse_btn.pack(pady=5)

        # Chọn file API key
        self.config_btn = ctk.CTkButton(self, text="Chọn file username và API Zotero (.txt)", command=self.browse_config_file)
        self.config_btn.pack(pady=10)

        self.config_label = ctk.CTkLabel(self, text="Chưa chọn file username và API Zotero", text_color="gray")
        self.config_label.pack(pady=5)

        # Bắt đầu xử lý
        self.run_btn = ctk.CTkButton(self, text="Bắt đầu", command=self.start_import, fg_color="#1e90ff")
        self.run_btn.pack(pady=15)

        self.status_label = ctk.CTkLabel(self, text="Trạng thái: Chờ bắt đầu", text_color="gray")
        self.status_label.pack(pady=5)

        self.log_box = ctk.CTkTextbox(self, height=250)
        self.log_box.pack(padx=10, pady=10, fill="both", expand=True)
        self.log_box.configure(state="disabled")

    def setup_logging(self):
        self.logger = logging.getLogger("AutoImport")
        self.logger.setLevel(logging.INFO)
        handler = TextHandler(self.log_box)
        self.logger.addHandler(handler)

    def browse_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.entry.delete(0, "end")
            self.entry.insert(0, path)

    def browse_config_file(self):
        path = filedialog.askopenfilename(
            title="Chọn file API and username.txt",
            filetypes=[("Text Files", "*.txt")]
        )
        if path:
            self.config_file_path = path
            self.config_label.configure(text=f"Đã chọn: {os.path.basename(path)}", text_color="green")

    def start_import(self):
        dir_path = self.entry.get().strip()
        if not os.path.isdir(dir_path):
            self.status_label.configure(text="❌ Thư mục không hợp lệ", text_color="red")
            return
        if not self.config_file_path or not os.path.isfile(self.config_file_path):
            self.status_label.configure(text="❌ Chưa chọn file cấu hình", text_color="red")
            return

        self.status_label.configure(text="🔄 Đang xử lý...", text_color="orange")
        threading.Thread(target=self.run_import, args=(dir_path,)).start()

    def run_import(self, root_dir):
        try:
            config = load_config(self.config_file_path)
            zot = zotero.Zotero(
                library_id=config["library_id"],
                library_type="user",
                api_key=config["api_key"]
            )
            main_import(root_dir, zot, self.logger)
            self.status_label.configure(text="✅ Hoàn tất", text_color="green")
        except Exception as e:
            self.logger.error(str(e))
            self.status_label.configure(text="❌ Có lỗi xảy ra", text_color="red")

# ========== Ghi log ra GUI ==========
class TextHandler(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        self.widget.configure(state="normal")
        self.widget.insert("end", msg + "\n")
        self.widget.configure(state="disabled")
        self.widget.yview("end")

# ========== Hàm xử lý chính ==========
def main_import(root_dir, zot, logger):
    logger.info("🔌 Đang kết nối tới Zotero...")
    zot.key_info()
    logger.info("✅ Kết nối thành công.")

    all_attachments = zot.everything(zot.items(itemType='attachment'))
    existing_paths = {item['data']['path'] for item in all_attachments if item['data'].get('linkMode') == 'linked_file'}

    all_collections = zot.collections()
    collections_by_parent = {}
    for coll in all_collections:
        parent = coll['data'].get('parentCollection', False)
        collections_by_parent.setdefault(parent, []).append(coll)

    def get_or_create_collection(name, parent_key=False):
        for coll in collections_by_parent.get(parent_key, []):
            if coll['data']['name'] == name:
                return coll['key']
        new_coll_data = {'name': name}
        if parent_key:
            new_coll_data['parentCollection'] = parent_key
        result = zot.create_collection([new_coll_data])
        new_coll = result['successful']['0']
        collections_by_parent.setdefault(parent_key, []).append({
            'key': new_coll['key'],
            'data': {'name': name, 'parentCollection': parent_key}
        })
        logger.info(f"📁 Tạo collection mới: {name}")
        return new_coll['key']

    root_name = os.path.basename(root_dir)
    root_key = get_or_create_collection(root_name)
    collection_keys = {root_dir: root_key}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        parent_key = collection_keys.get(dirpath)
        for subdir in dirnames:
            subdir_path = os.path.join(dirpath, subdir)
            subdir_key = get_or_create_collection(subdir, parent_key)
            if subdir_key:
                collection_keys[subdir_path] = subdir_key

        for filename in filenames:
            if filename.endswith(".pdf"):
                pdf_path = os.path.abspath(os.path.join(dirpath, filename))
                file_uri = "file:///" + pdf_path.replace("\\", "/")
                if file_uri in existing_paths:
                    logger.info(f"⚠️ Bỏ qua (đã có): {filename}")
                    continue
                item_data = {
                    'itemType': 'attachment',
                    'linkMode': 'linked_file',
                    'path': file_uri,
                    'title': filename,
                    'collections': [parent_key]
                }
                try:
                    zot.create_items([item_data])
                    logger.info(f"✅ Thêm: {filename}")
                    existing_paths.add(file_uri)
                    time.sleep(0.5)
                except Exception as e:
                    logger.error(f"❌ Lỗi khi thêm {filename}: {e}")

# ========== Khởi chạy GUI ==========
if __name__ == "__main__":
    app = App()
    app.mainloop()
