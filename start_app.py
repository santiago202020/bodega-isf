import subprocess
import time
import sys
import os

port = os.environ.get('PORT', '8000')

# Iniciar Gunicorn directamente
cmd = [
    'gunicorn', 'bodegaISF.wsgi:application',
    '--bind', f'0.0.0.0:{port}',
    '--workers', '1',
    '--timeout', '120'
]

print(f"Iniciando: {' '.join(cmd)}")
process = subprocess.Popen(cmd)

# Mantener proceso vivo
try:
    process.wait()
except KeyboardInterrupt:
    process.terminate()
sys.exit(process.returncode)