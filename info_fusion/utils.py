from datetime import datetime

def date_auto_completion(date_str: str) -> str:
    now = datetime.now()
    date_str = date_str.strip()
    d = datetime.strptime(date_str, '%m-%d %H:%M').date()
    
    now_month = now.month
    now_day = now.day
    d_month = d.month
    d_day = d.day
    if d_month > now_month:
        return datetime.strptime(date_str, '%m-%d %H:%M').strftime(f'{now.year}-%m-%d %H:%M:00')
    elif d_month == now_month and d_day >= now_day:
        return datetime.strptime(date_str, '%m-%d %H:%M').strftime(f'{now.year}-%m-%d %H:%M:00')
    return datetime.strptime(date_str, '%m-%d %H:%M').strftime(f'{now.year + 1}-%m-%d %H:%M:00')


if __name__ == '__main__':
    d = date_auto_completion(' 09-19 08:12 '.strip())
    print(d)