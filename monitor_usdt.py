import requests
import time
import os
from datetime import datetime

# ============================================
# CONFIGURACIÓN
# ============================================
TELEGRAM_BOT_TOKEN = os.getenv('BOT_TOKEN', 'TU_TOKEN_AQUI')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID', 'TU_CHAT_ID_AQUI')

# Configuración de alertas (puedes cambiar estos valores)
PRECIO_OBJETIVO_VENTA = float(os.getenv('PRECIO_VENTA', '50.0'))
PRECIO_OBJETIVO_COMPRA = float(os.getenv('PRECIO_COMPRA', '48.0'))
INTERVALO_VERIFICACION = int(os.getenv('INTERVALO', '60'))

# ============================================
# FUNCIONES
# ============================================

def obtener_precio_binance():
    """Obtiene el precio actual de USDT/VES desde Binance"""
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=USDTVES"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        precio = float(data['price'])
        return precio
    except Exception as e:
        print(f"❌ Error al obtener precio: {e}")
        return None

def enviar_mensaje_telegram(mensaje):
    """Envía un mensaje a través del bot de Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": mensaje,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print(f"✅ Mensaje enviado")
        return True
    except Exception as e:
        print(f"❌ Error al enviar mensaje: {e}")
        return False

def verificar_y_alertar(precio_actual, ultimo_estado):
    """Verifica si se debe enviar una alerta"""
    
    # Alerta de VENTA (precio alto)
    if precio_actual >= PRECIO_OBJETIVO_VENTA and not ultimo_estado['alerta_venta_enviada']:
        mensaje = f"""🚀 <b>ALERTA DE PRECIO - USDT/VES</b>

📈 El precio ha alcanzado el objetivo de VENTA
💰 Precio actual: {precio_actual:.2f} VES
🎯 Objetivo: {PRECIO_OBJETIVO_VENTA:.2f} VES

⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"""
        
        if enviar_mensaje_telegram(mensaje):
            ultimo_estado['alerta_venta_enviada'] = True
    
    # Alerta de COMPRA (precio bajo)
    if precio_actual <= PRECIO_OBJETIVO_COMPRA and not ultimo_estado['alerta_compra_enviada']:
        mensaje = f"""📉 <b>ALERTA DE PRECIO - USDT/VES</b>

💵 El precio ha alcanzado el objetivo de COMPRA
💰 Precio actual: {precio_actual:.2f} VES
🎯 Objetivo: {PRECIO_OBJETIVO_COMPRA:.2f} VES

⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"""
        
        if enviar_mensaje_telegram(mensaje):
            ultimo_estado['alerta_compra_enviada'] = True
    
    # Resetear alertas
    if PRECIO_OBJETIVO_COMPRA < precio_actual < PRECIO_OBJETIVO_VENTA:
        if ultimo_estado['alerta_venta_enviada'] or ultimo_estado['alerta_compra_enviada']:
            ultimo_estado['alerta_venta_enviada'] = False
            ultimo_estado['alerta_compra_enviada'] = False
            print("🔄 Alertas reseteadas")

def ejecutar_monitor():
    """Función principal"""
    print("=" * 50)
    print("🤖 MONITOR DE PRECIO USDT/VES")
    print("=" * 50)
    print(f"📊 Alerta VENTA: ≥ {PRECIO_OBJETIVO_VENTA:.2f} VES")
    print(f"📊 Alerta COMPRA: ≤ {PRECIO_OBJETIVO_COMPRA:.2f} VES")
    print(f"⏱️  Intervalo: {INTERVALO_VERIFICACION}s")
    print("=" * 50)
    
    estado_alertas = {
        'alerta_venta_enviada': False,
        'alerta_compra_enviada': False
    }
    
    # Mensaje de inicio
    mensaje_inicio = f"""🤖 <b>Monitor Iniciado</b>

📊 USDT/VES (Binance)
🎯 Alerta VENTA: ≥ {PRECIO_OBJETIVO_VENTA:.2f} VES
🎯 Alerta COMPRA: ≤ {PRECIO_OBJETIVO_COMPRA:.2f} VES

✅ Sistema activo"""
    
    enviar_mensaje_telegram(mensaje_inicio)
    
    try:
        while True:
            precio = obtener_precio_binance()
            
            if precio:
                timestamp = datetime.now().strftime('%H:%M:%S')
                print(f"[{timestamp}] 💵 Precio: {precio:.2f} VES")
                verificar_y_alertar(precio, estado_alertas)
            
            time.sleep(INTERVALO_VERIFICACION)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitor detenido")
        enviar_mensaje_telegram("🛑 <b>Monitor Detenido</b>")

if __name__ == "__main__":
    ejecutar_monitor()
```

### **2. `requirements.txt`**
```
requests==2.31.0