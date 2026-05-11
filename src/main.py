"""
main.py
Entry point untuk Email Recap Tool.

Pipeline:
  1. Baca semua .eml dari data/emails/
  2. Analisis tiap email dengan model Qwen lokal (via LM Studio)
     → Setiap email langsung disimpan ke outputs/json/ setelah diproses
  3. Tulis semua hasil ke outputs/email_recap.xlsx

Syarat sebelum menjalankan:
  - LM Studio terinstall dan berjalan
  - Model Qwen3 sudah di-load di LM Studio
  - Local server LM Studio sudah distart (port 1234)
"""

import sys
import urllib.request
from eml_reader import load_all_emails
from ai_analyzer import analyze_all_emails
from excel_writer import write_excel

EMAIL_FOLDER = "data/emails"
OUTPUT_FILE = "outputs/email_recap.xlsx"
LM_STUDIO_URL = "http://localhost:1234/v1/models"


def check_lm_studio_running():
    """Ping LM Studio. Keluar dengan pesan jelas kalau server belum jalan."""
    try:
        urllib.request.urlopen(LM_STUDIO_URL, timeout=3)
    except Exception:
        print("❌ LM Studio local server belum berjalan.")
        print("   → Buka LM Studio → Load model Qwen3 → Klik 'Start Server'")
        print("   → Default address: http://localhost:1234")
        sys.exit(1)


def main():
    print("🔍 Mengecek koneksi LM Studio...")
    check_lm_studio_running()
    print("   ✓ LM Studio aktif\n")

    # Step 1: Baca email
    print(f"📂 Membaca email dari: {EMAIL_FOLDER}")
    emails = load_all_emails(EMAIL_FOLDER)
    if not emails:
        print("Tidak ada email yang bisa diproses. Keluar.")
        return
    print(f"   Ditemukan {len(emails)} email\n")

    # Step 2: Analisis dengan Qwen (tiap email → JSON dulu)
    print("🤖 Menganalisis email dengan model Qwen lokal...")
    print("   (setiap email akan disimpan ke outputs/json/ setelah diproses)\n")
    analyzed = analyze_all_emails(emails)

    # Step 3: Tulis ke Excel
    print("\n📊 Menulis ke Excel...")
    write_excel(analyzed, OUTPUT_FILE)


if __name__ == "__main__":
    main()
