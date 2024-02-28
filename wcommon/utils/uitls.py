

def excel_value_to_str(code):
    if code is None :
        return  None 
    if isinstance(code, (int, str)):
        return str(code)
    else :
        "{:.0f}".format(code)
  

def tup_map_get_index(tup_list:[],val:str ):
    for i,v in tup_list:
        if val ==v:
            return i
    else :
        return 0 