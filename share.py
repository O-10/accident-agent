import subprocess
import time
import os
from pyngrok import ngrok

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("Iniciando servidor Streamlit...")
streamlit_proc = subprocess.Popen(
    ["python", "-m", "streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

time.sleep(5)

print("Creando tunel publico con ngrok...")
public_url = ngrok.connect(8501)
print(f"\n{'='*50}")
print(f"URL PUBLICA: {public_url}")
print(f"{'='*50}")
print("\nComparte esta URL con quien quieras.")
print("Presiona Ctrl+C para detener.\n")

try:
    streamlit_proc.wait()
except KeyboardInterrupt:
    print("\nDeteniendo...")
    streamlit_proc.terminate()
    ngrok.kill()
