"""
Ponto de entrada principal da aplicação FastAPI
Substitui o app.py do Streamlit
"""

import uvicorn
import sys
from pathlib import Path

# Adiciona o diretório atual ao path
sys.path.append(str(Path(__file__).parent))

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
