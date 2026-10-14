import os
import zipfile

def pack_extension():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dist_dir = os.path.join(base_dir, "dist")
    out_zip = os.path.join(base_dir, "smartconsent-extension.zip")

    if not os.path.exists(dist_dir):
        print(f"Error: Directory '{dist_dir}' not found. Please run 'npm run build' first.")
        return

    print(f"Packaging Chrome Extension from: {dist_dir}")
    print(f"Output target: {out_zip}\n")

    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(dist_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, dist_dir)
                zipf.write(abs_path, rel_path)
                print(f"  Included: {rel_path}")

    size_kb = os.path.getsize(out_zip) / 1024
    print(f"\nSuccess! Extension archive created ({size_kb:.1f} KB):")
    print(f"-> {out_zip}")

if __name__ == "__main__":
    pack_extension()
