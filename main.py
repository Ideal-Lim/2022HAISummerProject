from datetime import datetime


def printlog(message, *args):
    """인자로 받은 문자열을 파이썬 셸에 출력한다."""
    print(datetime.now().strftime('[%m/%d %H:%M:%S]'), message, *args)

if __name__ == '__main__':
    try:
        buy_percent = 0.19

        # Data 동기화
        

        while True:
            t_now = datetime.now()
            t_start = t_now.replace(hour=21, minute=30, second=0, microsecond=0)
            t_sell = t_now.replace(hour=10, minute=20, second=0, microsecond=0)
            t_exit = t_now.replace(hour=10, minute=30, second=0, microsecond=0)

        if t_start < t_now < t_sell :
            buy
    except Exception as ex:
        printlog(str(ex))