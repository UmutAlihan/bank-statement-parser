import slate
from datetime import datetime
import re
import pandas

with open("00158007306884271.pdf", "rb") as f:
    doc = slate.PDF(f) 
    
def validate_date(string):
    #print("The original string is : " + str(test_str))
    format = "%d.%m.%Y"
    try:
        res = bool(datetime.strptime(string, format))
        #print("This is a date: " + str(string))
    except ValueError:
        res = False
        #print("This is NOT a date: " + str(string))
    return res

def extract_page_data(page_items):
    page_items = [i.strip() for i in page_items]
    while '' in page_items:
        page_items.remove('')

    tmp_list = []
    grouped_kalem_list = []

    for i, page_item in enumerate(reversed(page_items)):
        #if page_item == '': page_items.remove(page_item)
        tmp_list.append(page_item)
        if validate_date(page_item):
            tmp_list = tmp_list[::-1] # [::-1] --> reverses the list
            tmp_dict = {
                        "tarih": tmp_list[0],
                        "saat": tmp_list[1],
                        "tutar": tmp_list[3],
                        "detay": " ".join(tmp_list[4:]) #re.sub(r'[0-9.,]+', '', tmp_list[4]),
                        #"detay": tmp_list[5]
                       }
            grouped_kalem_list.append(tmp_dict) 
            tmp_list = tmp_dict = []
    
    return grouped_kalem_list[::-1]

start_identifier = "BAKİYE İŞLEM ADI"
pages = []

for i, page in enumerate(doc):
    start_index = page.index(start_identifier) + len(start_identifier)
    page_items = list(filter(None, page[start_index:].split("\n")))
    page_data = extract_page_data(page_items)
    #print(f"page: {i} - first data: {page_data}")
    pages.append(page_data)

kalems_in_ekstre = []
for page in pages:
    for kalem in page:
        kalems_in_ekstre.append(kalem)

df_ekstre = pandas.DataFrame.from_records(kalems_in_ekstre)