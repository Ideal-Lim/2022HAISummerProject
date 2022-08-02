from datetime import datetime


def update_data():
    """Nasdaq 지수 데이터 최신화"""
    realtime_nasdaq = yf.download(tickers='^IXIC', interval='1m', period='1d')
    realtime_nasdaq.to_csv(f"./YfinanceData/nasdaq_{today_str}.csv")
    return realtime_nasdaq

def printlog(message, *args):
    """인자로 받은 문자열을 출력"""
    print(datetime.now().strftime('[%m/%d %H:%M:%S]'), message, *args)

if __name__ == '__main__':

    try:
        today_str = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        buy_percent = 0.19

        while True:
            t_now = datetime.now()
            t_start = t_now.replace(hour=21, minute=30, second=0, microsecond=0)
            t_sell = t_now.replace(hour=10, minute=20, second=0, microsecond=0)
            t_exit = t_now.replace(hour=10, minute=30, second=0, microsecond=0)

            # Data 동기화
            t_data = update_data()

        if t_start < t_now < t_sell :
            buy
    except Exception as ex:
        printlog(str(ex))