# k8s-pdf-docs
kubernetes.io/docs in PDF format

### Download the book
_In progress_

### Setup
```bash
virtualenv venv -p $(which python3)
source venv/bin/activate
pip install -r requirements.txt
```
You may also need to install [WeasyPrint](https://weasyprint.readthedocs.io/en/latest/install.html) additional dependencies depends on your OS.


### Usage
```bash
# to create an index file
python index.py

# To start downloading & converting to PDF
python process.py
# on macOS:
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES python process.py

# To stitch all downloaded PDFs and generate one single file
python stitch.py
```

Note that this is pretty slow process but it will continue from where it has left off if it stopped for any reason in the middle.
