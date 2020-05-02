""" INTRODUCTION """
# This files is to attain all information about the covid-19 pandemic, 
# for each country, and populate the database that will be accessed by Amazon Alexa and Google Home
""" INTRODUCTION """

""" DEPENDENCIES """
from bs4 import BeautifulSoup
import mysql.connector
import requests
import time
import country_converter as coco

""" DEPENDENCIES """

class Scraper:
    def __init__(self):
        self.viable_countries = {}
        self.URL_worldometers = 'https://www.worldometers.info/coronavirus/'
        self.worldometers_headers = {
            'authority': 'www.worldometers.info',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
        }

    # The page parameter will be a string '#' or 'country/name'
    def get_worldometers(self, page):
        manipulated_url = self.URL_worldometers + page  # Edited depending on the page parameter
        data = requests.get(manipulated_url, headers=self.worldometers_headers)
        response = data.content
        
        return response

    def collect_available_countries(self):
        self.viable_countries.clear()
        # Configuring BeautifulSoup
        response = self.get_worldometers('#')
        soup = BeautifulSoup(response, 'html.parser')
        
        # Finding table and removing rows, with style = {display: none}
        country_today_table = soup.find('table', {'id':'main_table_countries_today'})
        rows = country_today_table.find_all('tr')
        rows = rows[1:]
        for row in rows:
            if str(row).find('display: none') != -1:
                bad_index = rows.index(row)
                del rows[bad_index]
        
        # Facroting rows to get only country name and href
        for row in rows:
            country_element = row.find('td')
            country_name = country_element.text
            country_links = country_element.find_all('a', href=True)
            country_href = None
            for link in country_links:
                href = link.get('href')
                country_href = href
            self.viable_countries.update({country_name : country_href})
        
        # Factoring dictionary to make it only countries
        for name, href in list(self.viable_countries.items()):
            if href == None:
                delete_key = list(self.viable_countries.keys())[list(self.viable_countries.values()).index(None)]
                self.viable_countries.pop('{}'.format(delete_key))
        
        final_country_hrefs = list(self.viable_countries.values())
        fuzzy_country_names = list(self.viable_countries.keys())

        # Filtering countries
        for fuzzy_country in fuzzy_country_names:
            try:
                if fuzzy_country.find('S.') != -1:
                    altered_fuzzy = fuzzy_country.replace('S. ', '')
                    bad_index = fuzzy_country_names.index(fuzzy_country)
                    fuzzy_country_names[bad_index] = altered_fuzzy
                elif fuzzy_country == 'UAE':
                    altered_fuzzy = 'United Arab Emirates'
                    bad_index = fuzzy_country_names.index(fuzzy_country)
                    fuzzy_country_names[bad_index] = altered_fuzzy
                elif fuzzy_country == 'Ivory Coast':
                    altered_fuzzy = "Côte d'Ivoire"
                    bad_index = fuzzy_country_names.index(fuzzy_country)
                    fuzzy_country_names[bad_index] = altered_fuzzy
                elif fuzzy_country == 'Channel Islands':
                    # Channel islands is already inclided in the UK
                    del_index = fuzzy_country_names.index(fuzzy_country)
                    fuzzy_country_names.pop(del_index)
                    final_country_hrefs.pop(del_index)
                elif fuzzy_country == 'DRC':
                    altered_fuzzy = "Congo"
                    bad_index = fuzzy_country_names.index(fuzzy_country)
                    fuzzy_country_names[bad_index] = altered_fuzzy
                elif fuzzy_country == 'Faeroe Islands':
                    altered_fuzzy = "Faroe Islands"
                    bad_index = fuzzy_country_names.index(fuzzy_country)
                    fuzzy_country_names[bad_index] = altered_fuzzy
                elif fuzzy_country == 'Laos':
                    altered_fuzzy = "Lao People's Democratic Republic"
                    bad_index = fuzzy_country_names.index(fuzzy_country)
                    fuzzy_country_names[bad_index] = altered_fuzzy
                elif fuzzy_country.find('St.') != -1:
                    # Cannot be bothered
                    del_index = fuzzy_country_names.index(fuzzy_country)
                    fuzzy_country_names.pop(del_index)
                    final_country_hrefs.pop(del_index)
                elif fuzzy_country == 'Caribbean Netherlands':
                    # Channel islands is already inclided in the UK
                    del_index = fuzzy_country_names.index(fuzzy_country)
                    fuzzy_country_names.pop(del_index)
                    final_country_hrefs.pop(del_index)
                elif fuzzy_country == 'Saint Pierre Miquelon':
                    # Channel islands is already inclided in the UK
                    del_index = fuzzy_country_names.index(fuzzy_country)
                    fuzzy_country_names.pop(del_index)
                    final_country_hrefs.pop(del_index)
                elif fuzzy_country == 'UK':
                    altered_fuzzy = "United Kingdom"
                    bad_index = fuzzy_country_names.index(fuzzy_country)
                    fuzzy_country_names[bad_index] = altered_fuzzy
                elif fuzzy_country == 'CAR':
                    altered_fuzzy = "Central African Republic"
                    bad_index = fuzzy_country_names.index(fuzzy_country)
                    fuzzy_country_names[bad_index] = altered_fuzzy
                    
            except:
                print("    Could not convert --> {}".format(fuzzy_country))
        # Filtering countries

        final_country_names = coco.convert(names=fuzzy_country_names, to='ISO2', not_found=None)

        self.viable_countries.clear()

        for x in range(len(final_country_names)):
            self.viable_countries.update({final_country_names[x] : final_country_hrefs[x]})
        
        return self.viable_countries

    def global_stats(self):
        # Configuring BeautifulSoup
        response = self.get_worldometers('#')
        soup = BeautifulSoup(response, 'html.parser')

        # Getting main cases, deaths and recoveries
        main_counters = soup.find_all('div', {'class':'maincounter-number'})
        
        global_total_cases = int(str(main_counters[0].text).replace(',', ''))
        global_total_deaths = int(str(main_counters[1].text).replace(',', ''))
        global_total_recoveries = int(str(main_counters[2].text).replace(',', ''))

        global_active_cases = global_total_cases - (global_total_deaths + global_total_recoveries)

        return {'total_cases':global_total_cases, 'total_deaths':global_total_deaths, 'total_recoveries':global_total_recoveries, 'active_cases':global_active_cases}
    
    def country_stats(self, country):
        # Configuring BeautifulSoup
        country = country.replace('the ', '').replace(' the', '')
        
        try:
            manipulated_country_extension = self.collect_available_countries()[country]
        except:
            return 'CountryError'

        response = self.get_worldometers('{}'.format(manipulated_country_extension))
        soup = BeautifulSoup(response, 'html.parser')

        # Getting the country's cases, deaths and recoveries
        main_counters = soup.find_all('div', {'class':'maincounter-number'})
        
        country_total_cases = str(main_counters[0].text).replace(',', '')
        if country_total_cases.find("N/A") == -1:
            country_total_cases = int(country_total_cases)
        else:
            country_total_cases = "ScrapeError"
            # If the cases are not available, we will flag this country and reject all questions regarding it
        
        country_total_deaths = str(main_counters[1].text).replace(',', '')
        if country_total_deaths.find("N/A") == -1:
            country_total_deaths = int(country_total_deaths)
            calculation_deaths = country_total_deaths
        else:
            country_total_cases = "ScrapeError"
            calculation_deaths = country_total_deaths # So that the calculation for active cases does not fail
        
        country_total_recoveries = str(main_counters[2].text).replace(',', '')
        if country_total_recoveries.find("N/A") == -1:
            country_total_recoveries = int(country_total_recoveries)
            calculation_recoveries = country_total_recoveries
        else:
            country_total_recoveries = "ScrapeError"
            calculation_recoveries = 0 # So that the calculation for active cases does not fail

        
        country_active_cases = country_total_cases - (calculation_deaths + calculation_recoveries)

        return {'country_cases':country_total_cases, 'country_deaths':country_total_deaths, 'country_recoveries':country_total_recoveries, 'country_active':country_active_cases}