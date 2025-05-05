###############################################################################
# 1) ⚡ Brzi lokalni razvoj (bez Dockera)
###############################################################################
make run_backend      # FastAPI → http://127.0.0.1:8000
make run_frontend     # Streamlit → http://127.0.0.1:8501
# ili sve u jednom terminalu
make run

###############################################################################
# 2) 🐳 Docker način rada
###############################################################################
make docker-up        # build + pokreni backend & frontend kroz docker‑compose
make docker-down      # zaustavi i ukloni kontejnere

# pojedinačne slike / kontejneri
make build            # build‑a backend + frontend slike
make start            # pokrene ih (8000 / 8501)
make stop             # zaustavi
