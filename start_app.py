import subprocess
import time
import requests
import sys
import os

def main():
    port = os.environ.get('PORT', '8000')
    
    print("=" * 50)
    print("🚀 INICIANDO DJANGO EN RAILWAY")
    print("=" * 50)
    
    # 1. Iniciar Gunicorn
    gunicorn_cmd = [
        'gunicorn', 'bodegaISF.wsgi:application',
        '--bind', f'0.0.0.0:{port}',
        '--workers', '1',
        '--timeout', '300',
        '--preload',
        '--access-logfile', '-',
        '--error-logfile', '-'
    ]
    
    print(f"📡 Comando: {' '.join(gunicorn_cmd)}")
    proc = subprocess.Popen(gunicorn_cmd)
    
    # 2. Esperar carga inicial
    print("⏳ Esperando 40 segundos para carga de Django...")
    time.sleep(40)
    
    # 3. Verificar health check
    print("🔍 Realizando health check...")
    success = False
    for attempt in range(10):
        try:
            response = requests.get(f'http://localhost:{port}/', timeout=15)
            if response.status_code == 200:
                print(f"✅ HEALTH CHECK EXITOSO (intento {attempt+1})")
                print(f"📞 App respondiendo en: http://localhost:{port}")
                success = True
                break
        except Exception as e:
            print(f"⚠️  Intento {attempt+1} fallado: {str(e)}")
            time.sleep(5)
    
    if not success:
        print("❌ HEALTH CHECK FALLÓ después de 10 intentos")
        proc.terminate()
        sys.exit(1)
    
    # 4. Mantener app corriendo
    print("🎯 App desplegada exitosamente. Manteniendo contenedor activo...")
    proc.wait()

if __name__ == "__main__":
    main()