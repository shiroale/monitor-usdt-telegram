import requests
import time
import os
import statistics
from datetime import datetime

# ============================================
# CONFIGURATION
# ============================================
TELEGRAM_BOT_TOKEN = os.getenv('BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

# Timing configuration
CHECK_INTERVAL = int(os.getenv('INTERVALO', '60'))
# Send the detailed report every X checks
REPORT_EVERY_X_CHECKS = 10 

# ============================================
# FUNCTIONS
# ============================================

def get_binance_p2p_market_data():
    """
    Fetches the top 20 advertisements from Binance P2P 
    to analyze the price distribution.
    """
    try:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        payload = {
            "asset": "USDT",
            "fiat": "VES",
            "merchantCheck": False,
            "page": 1,
            "payTypes": [],
            "publisherType": None,
            "rows": 20, # Fetch more rows to get a real sample
            "tradeType": "BUY"
        }
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('data'):
            # Extract all prices from the 20 merchants
            prices = [float(adv['adv']['price']) for adv in data['data']]
            return prices
        return []
    except Exception as e:
        print(f"❌ Error fetching P2P data: {e}")
        return []

def send_telegram_notification(message):
    """Sends a formatted message to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Error: Telegram credentials missing")
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ Error sending Telegram message: {e}")
        return False

def analyze_and_report(prices, status):
    """Calculates High, Low, and Mode, then sends the report"""
    if not prices:
        return

    highest = max(prices)
    lowest = min(prices)
    
    # Calculate the 'Most Shown' price (Mode)
    try:
        most_shown = statistics.mode(prices)
    except statistics.StatisticsError:
        # If there's no single mode, take the most frequent or first
        most_shown = max(set(prices), key=prices.count)

    # Periodic Report Logic
    status['cycle_count'] += 1
    if status['cycle_count'] >= REPORT_EVERY_X_CHECKS:
        report_msg = (
            f"📊 <b>P2P Merchant Analysis (Top 20)</b>\n\n"
            f"🔺 <b>Highest:</b> {highest:.2f} VES\n"
            f"🔹 <b>Most Shown:</b> {most_shown:.2f} VES\n"
            f"🔻 <b>Lowest:</b> {lowest:.2f} VES\n\n"
            f"⏰ {datetime.now().strftime('%H:%M:%S')}"
        )
        send_telegram_notification(report_msg)
        status['cycle_count'] = 0

def run_monitor():
    """Main execution loop"""
    print("🤖 USDT/VES ADVANCED MONITOR STARTED")
    
    status = {'cycle_count': 0}
    
    start_msg = (
        f"✅ <b>Advanced Monitor Active</b>\n"
        f"Analyzing top 20 merchants every {CHECK_INTERVAL}s"
    )
    send_telegram_notification(start_msg)
    
    try:
        while True:
            prices = get_binance_p2p_market_data()
            if prices:
                # Log to console
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Data captured. "
                      f"Low: {min(prices):.2f} | High: {max(prices):.2f}")
                
                analyze_and_report(prices, status)
            
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("\n🛑 Monitor stopped")

if __name__ == "__main__":
    run_monitor()
