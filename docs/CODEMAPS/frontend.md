<!-- Generated: 2026-11-20 | Files scanned: 79 | Token estimate: ~142 -->
# Trainer interface

`app/streamlit_app.py` → `app/ui/app.py:main` → HTTP client → FastAPI.

The Streamlit session holds chat turns, active product and date filters, and form state. Answer rendering shows citations and provenance. The feedback form sends the original request and answer with the trainer's assessment. Review actions use a separate bearer token. PostgreSQL retains submitted feedback across EC2 stops.

On AWS, the trainer opens the UI on port 8501 from the saved /32. The UI container connects to the API at `http://api:8000` on the Compose network.
