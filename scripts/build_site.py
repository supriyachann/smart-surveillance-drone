"""Build only the public sample dashboard for GitHub Pages; no backend or secrets."""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
target = root / 'dist'
target.mkdir(exist_ok=True)
html = (root / 'static/index.html').read_text()
html = html.replace('<html lang="en">', '<html lang="en" data-mode="demo">')
(target / 'index.html').write_text(html)
for name in ('app.js', 'style.css'):
    shutil.copyfile(root / 'static' / name, target / name)
(target / '.nojekyll').touch()
print('Built sample dashboard in dist/ (synthetic data only)')
