# 🛠️ KiCad Mouser ZIP Import Tool

A Python tool for importing symbols, footprints, and 3D models from a **Mouser ZIP package** into an existing **KiCad library**.

---

## 📦 Purpose

This utility automates the process of:

- Extracting a Mouser ZIP archive containing KiCad files.
- Copying the **symbol** into an existing `.kicad_sym` library.
- Copying the **footprint** into a `.pretty` folder.
- Moving any **3D models (.step)** into a designated `3D` folder.
- Automatically cleaning up temporary files.

---

## 🚀 Usage

```bash
python import_kicad_mouser_zip.py [path_to_zip] [path_to_library_folder]
