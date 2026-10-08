"""Build a clean, deterministic web-upload bundle from this source checkout.

No upload is performed. Caches, generated artifacts, logs and local install
records are excluded. Run from the repository root:

    python tools/build_upload.py
"""
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dlm import __version__ as VERSION  # single source of truth

ARTIFACT_TAG = 'v0.000' + VERSION.split('.')[-1]

TOP_FILES = ('README.md', 'PRE_REGISTRATION.md', 'RESULTS.md', 'CHANGELOG.md',
             'CONTRIBUTING.md', 'PUBLICATION_CHECKLIST.md', 'LICENSE',
             'pyproject.toml', 'requirements.txt', '.gitignore', 'work.txt',
             'run_demo.py', 'probe_vram.py')
TOP_DIRS = ('dlm', 'tests', 'examples', 'tools', '.github')


def main():
    artifacts = ROOT / 'artifacts'
    target = artifacts / 'github_upload'
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    for name in TOP_FILES:
        shutil.copy2(ROOT / name, target / name)
    for name in TOP_DIRS:
        shutil.copytree(ROOT / name, target / name,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo', '*.egg-info'))
    hashes = {str(p.relative_to(target)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(target.rglob('*')) if p.is_file()}
    (target / 'SOURCE_MANIFEST.json').write_text(json.dumps({
        'schema': 'dlm-source-bundle-v1', 'version': VERSION,
        'excludes_self': True, 'sha256': hashes}, indent=2) + '\n')
    archive = artifacts / f'dlm_{ARTIFACT_TAG}_github_upload.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(target.rglob('*')):
            if p.is_file():
                info = zipfile.ZipInfo(str(p.relative_to(target)), (2020, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                z.writestr(info, p.read_bytes())
    with zipfile.ZipFile(archive) as z:
        expected = {str(p.relative_to(target)): p.read_bytes()
                    for p in target.rglob('*') if p.is_file()}
        actual = {name: z.read(name) for name in z.namelist()}
        assert actual == expected
    print(json.dumps({'zip': str(archive.relative_to(ROOT)), 'files': len(expected),
                      'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
                      'folder_zip_equal': True, 'uploaded': False}, indent=2))


if __name__ == '__main__':
    main()