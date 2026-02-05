from beacon.logs.logs import log_with_args, LOG
from beacon.conf.conf_override import config
from beacon.request.parameters import AlphanumericFilter

@log_with_args(config.level)
def iso8601_to_number(self, filter: AlphanumericFilter):
    days=0
    months=0
    years=0
    value_without_P=filter.value.replace('P', '')
    if 'Y' in value_without_P:
        numeric_split=value_without_P.split('Y')
        for num in numeric_split:
            if 'M' in num:
                months_split=num.split('M')
                for new_num in months_split:
                    if 'D' in new_num:
                        days=new_num.replace('D','')
                        days=int(days)
                    elif new_num != '':
                        months=new_num
                        months=int(months)
            elif 'D' in num:
                days=num.replace('D','')
                days=int(days)
            elif num != '':
                years=int(num)
    elif 'M' in value_without_P:
        numeric_split=value_without_P.split('M')
        for num in numeric_split:
            if 'D' in num:
                days=num.replace('D','')
                days=int(days)
            elif num != '':
                months=num
                months=int(months)
    elif 'D' in value_without_P:
        days=value_without_P.replace('D','')
        days=int(days)
    age_in_number=years+months/12+days/365.25
    return age_in_number