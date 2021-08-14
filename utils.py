import slate
from datetime import datetime
import re
import pandas as pd



class EkstreHandler:
    def __init__(self, ekstre_path):
        self.ekstre_path = ekstre_path
        with open(self.ekstre_path, "rb") as f:
            self.doc = slate.PDF(f) 
        self.parse()
    
    def validate_date(self, string):
        #print("The original string is : " + str(test_str))
        format = "%d.%m.%Y"
        try:
            res = bool(datetime.strptime(string, format))
            #print("This is a date: " + str(string))
        except ValueError:
            res = False
            #print("This is NOT a date: " + str(string))
        return res

    def extract_page_data(self, page_items):
        page_items = [i.strip() for i in page_items]
        while '' in page_items:
            page_items.remove('')

        tmp_list = []
        grouped_kalem_list = []

        for i, page_item in enumerate(reversed(page_items)):
            #if page_item == '': page_items.remove(page_item)
            tmp_list.append(page_item)
            if self.validate_date(page_item):
                tmp_list = tmp_list[::-1] # [::-1] --> reverses the list
                tmp_dict = {
                            "tarih": tmp_list[0],
                            "saat": tmp_list[1],
                            "tutar": float(tmp_list[3].replace(".","").replace(",",".")), # -> convert 10,000.00 to 10000.0
                            "detay": " ".join(tmp_list[4:]) #re.sub(r'[0-9.,]+', '', tmp_list[4]),
                            #"detay": tmp_list[5]
                           }
                grouped_kalem_list.append(tmp_dict) 
                tmp_list = tmp_dict = []

        return grouped_kalem_list[::-1]

    def parse(self):
        start_identifier = "BAKİYE İŞLEM ADI"
        pages = []

        for i, page in enumerate(self.doc):
            start_index = page.index(start_identifier) + len(start_identifier)
            page_items = list(filter(None, page[start_index:].split("\n")))
            page_data = self.extract_page_data(page_items)
            #print(f"page: {i} - first data: {page_data}")
            pages.append(page_data)

        kalems_in_ekstre = []
        for page in pages:
            for kalem in page:
                kalems_in_ekstre.append(kalem)

        self.ekstre = pd.DataFrame.from_records(kalems_in_ekstre)
        self.ekstre['tarih'] = pd.to_datetime(self.ekstre["tarih"], format="%d.%m.%Y")
        
        
    def write_to_excel(self, partial=None):
        if partial == None:
            self.ekstre.to_excel(f"ekstre_{self.ekstre_path}.xlsx")
        else:
            partial.to_excel(f"ekstre_partial.xlsx")
            
            
    def get_flow_diff(self, start, end):
        ekstre = self.ekstre[(self.ekstre['tarih'] >= start) & (self.ekstre['tarih'] <= end)]
    
        outflows = ekstre[ekstre["tutar"] < 0]
        total_outflow = outflows.tutar.sum()
    
        inflows = ekstre[ekstre["tutar"] >= 0]
        total_inflow = inflows.tutar.sum()
    
        diff = total_inflow + total_outflow
    
        print(f"{start}-{end} - In: {total_inflow} Out: {total_outflow} Diff: {diff}")
        return diff