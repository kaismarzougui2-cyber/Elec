#!/usr/bin/env python3
"""
Serveur d'upload simple pour ajouter les photos dans img/
Lancer avec : python3 upload_images.py
Puis ouvrir : http://localhost:8080/upload
"""
import http.server
import urllib.parse
import os
import cgi

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(UPLOAD_DIR, exist_ok=True)

HTML_FORM = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Upload photos – ELEC NESS</title>
<style>
  body { font-family: sans-serif; max-width: 600px; margin: 60px auto; padding: 0 20px; background: #2D2D2D; color: #fff; }
  h2 { color: #FFB800; }
  label { display: block; margin: 20px 0 6px; font-weight: bold; color: #FFB800; }
  input[type=file] { width: 100%; padding: 10px; background: #444; border: 2px dashed #FFB800; border-radius: 8px; color: #fff; }
  button { margin-top: 24px; width: 100%; background: #FFB800; color: #2D2D2D; font-weight: bold; font-size: 1rem; padding: 14px; border: none; border-radius: 8px; cursor: pointer; }
  .msg { margin-top: 20px; padding: 14px; border-radius: 8px; }
  .ok { background: #22c55e22; border: 1px solid #22c55e; color: #22c55e; }
  .err { background: #ef444422; border: 1px solid #ef4444; color: #ef4444; }
</style>
</head>
<body>
<h2>⚡ Ajouter les photos – ELEC NESS</h2>
<p>Sélectionnez vos deux photos pour les ajouter au site.</p>
<form method="POST" enctype="multipart/form-data">
  <label>Photo 1 – Éclairage extérieur (maison la nuit)</label>
  <input type="file" name="exterieur" accept="image/*" required>
  <label>Photo 2 – Éclairage intérieur (lustre)</label>
  <input type="file" name="interieur" accept="image/*" required>
  <button type="submit">⬆️ Envoyer les photos</button>
</form>
{message}
</body>
</html>"""


class UploadHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(fmt % args)

    def do_GET(self):
        if self.path in ("/", "/upload"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_FORM.format(message="").encode())
        else:
            # Serve static files from project directory
            base = os.path.dirname(__file__)
            filepath = os.path.join(base, self.path.lstrip("/"))
            if os.path.isfile(filepath):
                self.send_response(200)
                if filepath.endswith(".html"):
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                elif filepath.endswith((".jpg", ".jpeg")):
                    self.send_header("Content-Type", "image/jpeg")
                elif filepath.endswith(".png"):
                    self.send_header("Content-Type", "image/png")
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404)

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.get("Content-Type", ""))
        if ctype != "multipart/form-data":
            self.send_error(400)
            return

        pdict["boundary"] = bytes(pdict["boundary"], "utf-8")
        fields = cgi.parse_multipart(self.rfile, pdict)

        saved = []
        errors = []

        for field, filename in [("exterieur", "eclairage-exterieur.jpg"),
                                  ("interieur", "eclairage-interieur.jpg")]:
            data = fields.get(field)
            if data and data[0]:
                path = os.path.join(UPLOAD_DIR, filename)
                with open(path, "wb") as f:
                    f.write(data[0])
                saved.append(filename)
            else:
                errors.append(field)

        if saved and not errors:
            msg = f'<div class="msg ok">✅ Photos enregistrées : {", ".join(saved)}<br>Vous pouvez maintenant ouvrir <a href="/index.html" style="color:#22c55e">index.html</a> pour voir le résultat.</div>'
        else:
            msg = f'<div class="msg err">❌ Erreur pour : {", ".join(errors)}</div>'

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_FORM.format(message=msg).encode())


if __name__ == "__main__":
    port = 8080
    server = http.server.HTTPServer(("0.0.0.0", port), UploadHandler)
    print(f"✅ Serveur démarré sur http://localhost:{port}/upload")
    print("   Ouvrez ce lien dans votre navigateur pour uploader les photos.")
    print("   Ctrl+C pour arrêter.")
    server.serve_forever()
