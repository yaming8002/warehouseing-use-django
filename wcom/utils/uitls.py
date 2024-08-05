from datetime import datetime, timedelta
import re

def excel_value_to_str(code,desired_length=None):
    if code is None :
        return  None
    if isinstance(code, str):
        return None if code.strip() == '' else str(code).strip()
    elif desired_length :
        return "{:.0f}".format(code).zfill(desired_length)
    else :
        return "{:.0f}".format(code)

def excel_num_to_date(excel_num):
    # Excel中的起始日期
    excel_epoch = datetime(1900, 1, 1)
    delta = timedelta(days=excel_num - 2)
    actual_date = excel_epoch + delta
    return actual_date

def tup_map_get_index(tup_list:[],val:str ):
    for i,v in tup_list:
        if val ==v:
            return i
    else :
        return 0

def get_month_range(today=None):

    today = today if today else datetime.date.today()
    first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month = first_day_of_month + timedelta(days=31)
    last_day_of_month = datetime(next_month.year, next_month.month, 1, 23, 59, 59) - timedelta(days=1)
    return [first_day_of_month, last_day_of_month]


def get_year_month(year_month=None):
    """_summary_

    Args:
        year_month (_type_): str

    Returns:
        _type_: _description_
    """
    year_month =year_month if year_month else (datetime.now()).strftime('%Y-%m')
    split_year_month = [int(x) for x in year_month.split('-')]
    return split_year_month[0],split_year_month[1]


def get_before_year_month(year=None,month=None):
    if year is None :
        year , month = get_year_month()
    month -= 1
    if month == 0:
        year -= 1
        month =12
    return year,month


def is_whse_code(s):
    pattern = r'^[A-Z][0-9]{6}$'
    if re.match(pattern, s):
        return True
    else:
        return False
