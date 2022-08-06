secs = ' Секунд'
mins = ' Минут'
hrs = ' Час'
def word_case(string,count):
    
    if 'Секунд' in string:
        if count in [1,21,31,41,51]:
            return str(count)+' Секунда'
        elif count in [2,3,4,22,23,24,32,33,34,42,43,44,52,53,54]:
            return str(count)+' Секунды'
        else:
            return str(count)+' Секунд'
    if 'Минут' in string:
        if count in [1,21,31,41,51]:
            return str(count)+' Минута'
        elif count in [2,3,4,22,23,24,32,33,34,42,43,44,52,53,54]:
            return str(count)+' Минуты'
        else:
            return str(count)+' Минут'
    if 'Час' in string:
        if count in [1,21]:
            return str(count)+' Час'
        elif count in [2,3,4,22,23]:
            return str(count)+' Часа'
        else:
            return str(count)+' Часов'

def calculate_time(raw):
    if raw < 60:
        seconds = raw
        string = word_case(secs,seconds)
        return string
    if raw >= 60 and raw < 3600:
        minutes = raw // 60
        seconds = raw % 60
        if seconds == 0:
            string = word_case(mins,minutes)
        else:
            string = word_case(mins,minutes)+' : '+word_case(secs,seconds)
        return string
    if raw >= 3600 and raw < 86401:
        hours = raw // 3600
        minutes = (raw-hours*3600) // 60
        seconds = raw % 60
        if seconds == 0:
            string = word_case(hrs,hours)+' : '+word_case(mins,minutes)
            if seconds == 0 and minutes == 0:
               string = word_case(hrs,hours)
            if minutes == 0:
                string = word_case(hrs,hours)+' : '+word_case(secs,seconds)
        else: 
            string = word_case(hrs,hours)+' : '+word_case(mins,minutes)+' : '+word_case(secs,seconds)
        return string 
