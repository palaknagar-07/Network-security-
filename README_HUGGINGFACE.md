# Hugging Face Spaces Deployment

Use this path if you want a low-risk ML demo deployment without AWS.

## Files to upload

Create a new Hugging Face Space with:

- SDK: `Gradio`
- Visibility: Public or Private

Then upload these project files/folders:

- `hf_app.py` as `app.py`
- `requirements-hf.txt` as `requirements.txt`
- `NetworkSecurity/`
- `final_model/`
- `data_schema/`
- `Valid_data/test.csv` if you want a sample CSV for testing

You do not need MongoDB credentials for the prediction-only demo.

## Why use the Hugging Face app

The existing `app.py` is a FastAPI app and includes training/database code. For a public demo, the safer approach is prediction-only:

- no public `/train` endpoint
- no MongoDB secret required
- no always-on EC2 instance
- simple CSV upload and CSV download

## Local test

```bash
pip install -r requirements-hf.txt
python hf_app.py
```

Then open the local Gradio URL and upload `Valid_data/test.csv`.
