import os
import time
from pyzotero import zotero
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main(root_dir):
    # Kết nối với Zotero API
    try:
        zot = zotero.Zotero(library_id='16199754', library_type='user', api_key='7h3vzXE3oXMgFFNS7KfmEUdL')
        # Kiểm tra quyền API
        logger.info("Kiểm tra quyền API...")
        zot.key_info()  # Gọi để xác minh API key
        logger.info("API key hợp lệ.")
    except Exception as e:
        logger.error(f"Lỗi khi kết nối với Zotero API: {e}")
        return

    # Lấy tất cả các attachment hiện có với linkMode='linked_file'
    try:
        logger.info("Lấy danh sách attachment hiện có...")
        all_attachments = zot.everything(zot.items(itemType='attachment'))
        existing_paths = {item['data']['path'] for item in all_attachments if item['data'].get('linkMode') == 'linked_file'}
        logger.info(f"Tìm thấy {len(existing_paths)} attachment hiện có.")
    except Exception as e:
        logger.error(f"Lỗi khi lấy attachment: {e}")
        return

    # Lấy tất cả các collection hiện có
    try:
        logger.info("Lấy danh sách collection hiện có...")
        all_collections = zot.collections()
        logger.info(f"Tìm thấy {len(all_collections)} collection hiện có.")
    except Exception as e:
        logger.error(f"Lỗi khi lấy collections: {e}")
        return

    # Tạo từ điển để tra cứu collection theo parent
    collections_by_parent = {}
    for coll in all_collections:
        parent = coll['data'].get('parentCollection', False)
        if parent not in collections_by_parent:
            collections_by_parent[parent] = []
        collections_by_parent[parent].append(coll)

    # Hàm lấy hoặc tạo collection
    def get_or_create_collection(name, parent_key=False):
        collections = collections_by_parent.get(parent_key, [])
        for coll in collections:
            if coll['data']['name'] == name:
                return coll['key']
        # Nếu không tìm thấy, tạo mới
        try:
            new_coll_data = {'name': name}
            if parent_key:
                new_coll_data['parentCollection'] = parent_key
            result = zot.create_collection([new_coll_data])
            new_coll = result['successful']['0']
            logger.info(f"Tạo collection mới: {name}")
            # Cập nhật từ điển collections_by_parent
            if parent_key not in collections_by_parent:
                collections_by_parent[parent_key] = []
            collections_by_parent[parent_key].append({
                'key': new_coll['key'],
                'data': {'name': name, 'parentCollection': parent_key}
            })
            return new_coll['key']
        except Exception as e:
            logger.error(f"Lỗi khi tạo collection '{name}': {e}")
            return None

    # Bắt đầu với thư mục gốc
    root_name = os.path.basename(root_dir)
    root_key = get_or_create_collection(root_name)
    if not root_key:
        logger.error("Không thể tạo collection gốc, thoát.")
        return
    collection_keys = {root_dir: root_key}

    # Quét toàn bộ thư mục
    for dirpath, dirnames, filenames in os.walk(root_dir):
        parent_key = collection_keys.get(dirpath)
        if not parent_key:
            logger.warning(f"Không tìm thấy collection cho thư mục {dirpath}, bỏ qua.")
            continue

        # Tạo subcollection cho các thư mục con
        for subdir in dirnames:
            subdir_path = os.path.join(dirpath, subdir)
            subdir_key = get_or_create_collection(subdir, parent_key)
            if subdir_key:
                collection_keys[subdir_path] = subdir_key
            else:
                logger.warning(f"Bỏ qua thư mục con {subdir} do lỗi tạo collection.")

        # Xử lý các file PDF
        for filename in filenames:
            if filename.endswith('.pdf'):
                pdf_path = os.path.abspath(os.path.join(dirpath, filename))
                
                # Sửa lỗi f-string với backslash
                file_uri = 'file:///' + pdf_path.replace('\\', '/')
                
                if file_uri in existing_paths:
                    logger.info(f"Đã tồn tại item cho {pdf_path}, bỏ qua.")
                    continue
                
                # Tạo item mới với liên kết đến PDF
                item_data = {
                    'itemType': 'attachment',
                    'linkMode': 'linked_file',
                    'path': file_uri,
                    'title': filename,
                    'collections': [parent_key]
                }
                
                try:
                    zot.create_items([item_data])
                    logger.info(f"Đã thêm item cho {pdf_path}")
                    # Cập nhật để không thêm lại trong cùng một phiên
                    existing_paths.add(file_uri)
                    time.sleep(0.5)  # Tạm dừng để tránh vượt giới hạn API
                except Exception as e:
                    logger.error(f"Lỗi khi thêm item cho {pdf_path}: {e}")

if __name__ == '__main__':
    root_dir = input("Nhập đường dẫn thư mục gốc để quét: ")
    if not os.path.isdir(root_dir):
        logger.error("Thư mục không tồn tại. Vui lòng kiểm tra lại.")
    else:
        main(root_dir)