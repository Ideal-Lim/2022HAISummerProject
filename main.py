import time
import os
import json
import yfinance as yf
from datetime import datetime, timedelta
from hai_stock import OrderTypes, HAIStock

def printlog(message, *args):
    """인자로 받은 문자열을 출력"""
    print(datetime.now().strftime('[%m/%d %H:%M:%S]'), message, *args)

def update_data(ticker):
    """데이터 최신화 """
    if ticker == '^IXIC':
        realtime_data = yf.Ticker(ticker).history(interval='1m', period='1d') #^IXIC -> Nasdaq 지수
        realtime_data.to_csv(f"./YfinanceData/Nasdaq/nasdaq_{today_str}.csv")
    else :
        realtime_data = yf.Ticker(ticker).history(interval='1m', period='1d')  # ^IXIC -> Nasdaq 지수
        realtime_data.to_csv(f"./YfinanceData/{ticker}/{ticker}_{today_str}.csv")
    return realtime_data

def get_current_price(ticker):
    """종목의 현재가를 반환한다."""
    try :
        return yf.Ticker(ticker).history(period='1d', interval='1m').iloc[-1]['Close']
    except Exception as ex :
        printlog(ex)

def get_account_deposit(stock:HAIStock):
    """주문 가능한 금액(예산)을 확인한다."""
    deposit = stock.account_info()['deposit']
    return deposit

def get_my_stock(stock:HAIStock):
    """소유한 주식 정보를 확인한다."""
    my_stock = stock.account_info()['stock']
    return my_stock

def get_target_price(ticker):
    """매수 목표가를 반환한다. 매수 목표가 = 금일 시작 가격 + (어제 최고가 - 어제 최저가) * k"""
    try:
        tqqq_day = yf.Ticker(ticker).history(period='90d') #TQQQ 1day data
        lastday_high = tqqq_day.iloc[-2]['High']
        lastday_low = tqqq_day.iloc[-2]['Low']
        today_open = tqqq_day.iloc[1]['Open']
        target_price = today_open + (lastday_high - lastday_low) * 0.4
        return target_price
    except Exception as ex :
        printlog(ex)

def get_movingaverage(window):
    tqqq_day = yf.Ticker('TQQQ').history(period='90d')  # TQQQ 1day data
    return tqqq_day['Close'].rolling(window=window).mean().iloc[-1]

def buy_tqqq(stock: HAIStock):
    """tqqq 풀매수"""
    try:
        buy_qty = get_account_deposit(stock) // cur_tqqq # 매수 수량
        price = cur_tqqq * 1.0001 # 매수가
        num = stock.send_order(OrderTypes.BUY, 'TQQQ', buy_qty, price)
        printlog(f'[주문번호 : {num}] 가격 : {price}, 수량: {buy_qty} 매수 주문 신청')
        return num
    except:
        printlog("주문 불가")

def sell_tqqq(stock: HAIStock):
    try:
        my_stock_qty = get_my_stock()['share']
        price = cur_tqqq * 0.9998 # 매도가
        num = stock.send_order(OrderTypes.SELL, 'TQQQ', my_stock_qty, price)
        printlog("판매")
    except:
        printlog("주문 불가")

if __name__ == '__main__':
    try:
        """주식 서버 연결"""
        with open('config.json', 'rt') as f :
            CONFIG = json.load(f)
        stock = HAIStock(CONFIG['server'], CONFIG['token'])
        # 오늘 날짜 : 미국 증시 시간으로 맞춰줌 ex) 한국 2022-8-3 00:30 -> 미국 2022-8-2 11:30
        today_str = (datetime.now() - timedelta(hours=13)).strftime('%Y-%m-%d')
        # 목표가
        target_price = get_target_price('TQQQ')

        order_position = False  # 주문 여부
        order_check_time = 'None' # 주문 후 10분 후 시간
        buy_position = False # 매수 성공 여부

        while True:
            t_now = datetime.now()
            # 매수시간 매도시간
            t_buy_start = t_now.replace(hour=22, minute=30, second=0, microsecond=0)
            t_buy_end = t_now.replace(hour=4, minute=50, second=0, microsecond=0)
            t_sell_start = t_now.replace(hour=4, minute=58, second=00, microsecond=0)
            t_exit = t_now.replace(hour=5, minute=00, second=0, microsecond=0)

            # TQQQ 데이터 동기화
            save_tqqq = update_data('TQQQ')
            # 현재 TQQQ 종가 정보 가저옴
            cur_tqqq = get_current_price('TQQQ')

            # 5일, 10일 이동 평균선
            ma5 = get_movingaverage(5)
            ma10 = get_movingaverage(10)

            # 매수 여부 확인
            if t_now.strftime('%H:%M') == order_check_time and order_position is True: # 주문하고 10분 후 체크
                if len(get_my_stock(stock)) != 0:
                    buy_position = True # 매수 성공
                else:
                    order_position = False # 매수 실패

            """Process"""
            if not order_position: # 주문하지 않은 경우
                if t_buy_start < t_now < t_buy_end : # 22:30 ~ 4:50 사이
                    if cur_tqqq > target_price and cur_tqqq > ma5 and cur_tqqq > ma10:
                        order = buy_tqqq(stock) # 매수
                        order_time = (t_now + timedelta(minutes=10)).strftime('%H:%M')
                        order_position = True

            # 시장 마감 전 전량 매도
            if t_sell_start < t_now < t_exit : # 4:58 ~ 5:00 사이
                sell_tqqq(stock) # 매도
                time.sleep(5)
                os.system('shutdown -s -f') # 종료
            time.sleep(60)
    except Exception as ex:
        printlog(str(ex))