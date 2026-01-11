# Monitor de Precio USDT/VES

Bot que monitorea el precio de USDT/VES en Binance y envía alertas a Telegram.

## Variables de entorno necesarias:
- `BOT_TOKEN`: Token del bot de Telegram
- `CHAT_ID`: ID del chat de Telegram
- `PRECIO_VENTA`: Precio objetivo de venta (opcional, default: 50.0)
- `PRECIO_COMPRA`: Precio objetivo de compra (opcional, default: 48.0)
- `INTERVALO`: Segundos entre verificaciones (opcional, default: 60)
