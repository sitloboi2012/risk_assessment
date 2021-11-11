from __future__ import annotations
from abc import abstractmethod, ABC
from logging import warning


import pdfplumber
import camelot
from PyPDF2 import PdfFileReader


class BaseOCR(ABC):
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
    
    @abstractmethod
    def key_information_extraction(self):
        pass

    @abstractmethod
    def preprocessing(self):
        pass

    @abstractmethod
    def load_and_read_pdf(self):
        pass
    

class Covid_Schema(BaseOCR):
    def __init__(self, pdf_path):
        super().__init__(pdf_path)
        self.result = {}

    def load_and_read_pdf(self):
        with pdfplumber.open(self.pdf_path) as pdf:
            self.raw_tables = [
                tables
                for page in pdf.pages
                for tables in page.extract_tables()
            ]
        result = self.key_information_extraction()

        return result
    
    def preprocessing(self, text):
        result = [int(s) for s in text.split() if s.isdigit()]
        return result[0]
    
    def key_information_extraction(self):
        for major_table in self.raw_tables:
            for minor_table in major_table:

                if "Organisation Details" in minor_table:
                    for rows in major_table[1:]:
                        if "Organisation" in rows:
                            self.result["Organisation Name"] = rows[1]
                        elif "City" in rows:
                            self.result["City"] = rows[1]
                        elif "Postcode" in rows:
                            self.result["Postcode"] = rows[1]
                        elif "Country" in rows:
                            self.result["Country"] = rows[1]
                        elif "Client Representative" in rows:
                            self.result["Client Representative"] = rows[1]

                if "Critical Nonconformities" in minor_table:
                    self.result["Critical Nonconformities"] = minor_table[1]
                elif "Major Nonconformities" in minor_table:
                    self.result["Major Nonconformities"] = minor_table[1]
                elif "Minor Nonconformities" in minor_table:
                    self.result["Minor Nonconformities"] = self.preprocessing(minor_table[1])
                elif "Audit Recommendation" in minor_table:
                    self.result["Audit Recommendation"] = minor_table[1]
                elif "CB Name and Location" in minor_table:
                    self.result["CB Name and Location"] = minor_table[1]

                for rows in major_table:
                    if "Audit Type" in rows:
                        if len(rows) == 2:
                          self.result["Audit Type"] =  rows[1]
                        else:
                          self.result["Previous Audit Type"] = rows[2]
        
        return self.result


class AIBI_Schema():
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.result = {}
    
    def load_and_read_pdf(self):
        with open(self.pdf_path, "rb") as file:
            reader = PdfFileReader(file)
            pdf_length = reader.getNumPages()
            for page in range(pdf_length):
                self.tables = camelot.read_pdf(self.pdf_path, pages = str(page))
                self.key_information_extraction()
            file.close()
        
        with pdfplumber.open(self.pdf_path) as file:
            text = file.pages[2].extract_text().split("\n")
            self.extract_non_conformities(text)
            file.close()
        
        with pdfplumber.open(self.pdf_path) as file:
            for i in range(20,36):
                text = file.pages[i].extract_text().split("\n")
                self.extract_audit_recommendation(text)

        return self.result
    def key_information_extraction(self):
        for table in range(self.tables.n):
            dataframe = self.tables[table].df
            table_header = dataframe.iloc[0,0]
        
            if table_header == "Registered legal name" and "General description of organization" in list(dataframe.iloc[:,0]):
                organisation_name = dataframe.iloc[0,1].split("-")
                self.result["City"] = organisation_name[1]
                self.result["Organization name"] = organisation_name[0]
                self.result["Location"] = dataframe.iloc[3,1]
                self.result["Contact Person"] = dataframe.iloc[4,1]
        
            elif table_header == "Audit type":
                self.result["Prev Audit type"] = dataframe.iloc[0,1]
                self.result["Prev Audit date"] = dataframe.iloc[1,1]
                self.result["CB name"] = "AIBI-CS"

            elif "CB Name and office location" in list(dataframe.iloc[:,0]):
                self.result["CB Office Location"] = str(dataframe.iloc[2,3]) + " " + str(dataframe.iloc[3,3]) + " "+ str(dataframe.iloc[4,3]) +" "+ str(dataframe.iloc[5,3]) + " " + str(dataframe.iloc[6,3])

        return self.result
    
    def extract_non_conformities(self, text):
        for i in text:
            if "Critical nonconformities" in i:
                i = i.split(" ")
                i = i[-1]
                self.result["Critical nonconformities"] = i
            elif "Major nonconformities" in i:
                i = i.split(" ")
                i = i[-1]
                self.result["Major nonconformities"] = i
            elif "Minor nonconformities" in i:
                i = i.split(" ")
                i = i[-1]
                self.result["Minor nonconformities"] = i

    def extract_audit_recommendation(self, text):
        for i in text:
            if "Conclusion" in i:
                self.result["Audit Type"] = "Surveillance audit"
                self.result["Audit Recommendation"] = i.split(" ")[1:]

class FSSC_Version_5_Schema():
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.result = {}

    def load_and_read_pdf(self):
        with open(self.pdf_path, "rb") as file:
            reader = PdfFileReader(file)
            pdf_length = reader.getNumPages()
            for page in range(pdf_length):
                self.tables = camelot.read_pdf(self.pdf_path, pages = str(page))
                self.key_information_extraction()
        return self.result
    
    def key_information_extraction(self):
        for table in range(self.tables.n):
                dataframe = self.tables[table].df
                table_header = dataframe.iloc[0,0]

                if table_header == "Organization profile":
                    self.result["Organisation Name"] = dataframe.iloc[2,1]
                    self.result["City"] = dataframe.iloc[6,1]
                    self.result["Region"] = dataframe.iloc[7,1]
                    self.result["Postal Code"] = dataframe.iloc[8,1]
                    self.result["Country"] = dataframe.iloc[9,1]
                    self.result["Contact Person"] = dataframe.iloc[10,1]
                
                elif table_header == "Audit details":
                    self.result["CB Name and Location"] = dataframe.iloc[1,1]
                    self.result["Audit Type"] = dataframe.iloc[6,1]
                
                #elif table_header == "Audit team":
                #    audit_name.append(list(dataframe.iloc[2:,1].unique()))
                
                #elif table_header == "Audit scope":
                #    self.result["Food Sector"] = dataframe.iloc[1,1]
                
                elif table_header == "Audit details previous audit":
                    self.result["Prev Audit Type"] = dataframe.iloc[1,1]
                
                elif table_header == "Summary of audit findings":
                    self.result["Critical Nonconformities"] = dataframe.iloc[1,1]
                    self.result["Major Nonconformities"] = dataframe.iloc[2,1]
                    self.result["Minor Nonconformities"] = dataframe.iloc[3,1]
                
                elif table_header == "Audit recommendation":
                    self.result["Audit Recommendation"] = dataframe.iloc[1,0]
          
        
        return self.result