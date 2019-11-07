import datetime

def format_timestamp(time_str, time_zone):
    return datetime.datetime.strptime(time_str, '%Y-%m-%d').astimezone(tz=time_zone)
