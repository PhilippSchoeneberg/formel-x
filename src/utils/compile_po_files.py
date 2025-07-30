import os
import polib


base_dir = "assets"
for lang_code in os.listdir(base_dir):
    lang_dir = os.path.join(base_dir, lang_code, "LC_MESSAGES")
    if os.path.isdir(lang_dir):
        po_path = os.path.join(lang_dir, "texts.po")
        mo_path = os.path.join(lang_dir, "texts.mo")
        if os.path.exists(po_path):
            try:
                po = polib.pofile(po_path)
                po.save_as_mofile(mo_path)
                print(f"Compiled: {po_path} → {mo_path}")
            except Exception as e:
                print(f"Failed to compile {po_path}: {e}")
