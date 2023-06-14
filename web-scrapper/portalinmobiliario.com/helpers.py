from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException

from numpy.core.fromnumeric import amin
import requests
from bs4 import BeautifulSoup
from datetime import date
from datetime import datetime
import re 
import numpy as np 
import pandas as pd 
from IPython.display import clear_output
from time import sleep, time

import sys

import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Code execution timed out.")

def webscraping_deptos(region,pages,type,scope,rango_precio):  
    print(rango_precio)
    urls = []
    titles = []
    address = []
    prices = []
    publication_date = []

    '''
    total_m2 = []
    util_m2 = []
    rooms = []
    toilets = []
    amenities = []
    ambiances = []
    other_features = []
    description = []
    parking = []
    common_spends = []
    olds = []
    garage = []
    orientation = []
    floors_numbers = []
    apartment_floor_number = []
    apartments_per_floor = []
    '''
    highlighted_common_expenses = []
    highlighted_characteristics = []
    number_highlighted_characteristics = []

    print("Web Scraping Portal Inmobiliario")

    print(f"Buscando {type} para {scope}....")


    #Iterar por pagina para encontrar las urls de cada oferta de depto y almacenar los resultados en una lista llamada urls
    for i in range(1,pages*50,50):
        #main_url = 'https://www.portalinmobiliario.com/'+scope.lower().replace(" ","-")+'/'+type+'/'+region+'/_Desde_'+ str(i)

        main_url = 'https://www.portalinmobiliario.com/'+scope.lower().replace(" ","-")+'/'+type+'/'+region+'/_Desde_'+ str(i)+rango_precio
        #print(main_url)
        #driver.get(main_url)
        
        main_response = requests.get(main_url)
        sleep(0.05)
        main_soup = BeautifulSoup(main_response.text,'html.parser')
        #main_soup = BeautifulSoup(driver.page_source, 'html.parser')
        containers = main_soup.find_all('li',{'class':'ui-search-layout__item'})
        #ui-search-result__content ui-search-link
        for container in containers: 
            urls.append(container.find('a',class_='ui-search-result__content-wrapper ui-search-link')['href'])



        
    counter = 0
    
    # Initialize the driver and load the webpage
    driver = webdriver.Chrome()
    sleep(10)

    for url in urls:
        #print(url)
        #response = requests.get(url,allow_redirects=False)
        #driver.get(url)
        #sleep(0.2)
        #soup = BeautifulSoup(driver.page_source, 'html.parser')

        max_retries = 10
        retry_delay = 0.05
        timeout = 20
        # Set the timeout duration
        timeout_duration = 30

        # Set the signal handler
        signal.signal(signal.SIGALRM, timeout_handler)

        for _ in range(max_retries):
            try:         
                signal.alarm(timeout_duration)   
                driver.set_page_load_timeout(10)   
                driver.get(url)
                sleep(retry_delay)
                print("get:" + url)
                WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                print("soup completed")
                break  # Break out of the loop if the code runs without error
            except TimeoutException:
                print("Page load timed out.")
                retry_delay += 0.1  # Increase the retry delay for the next attempt
                driver.quit()
                sleep(retry_delay)
                driver = webdriver.Chrome()
            except TimeoutError:
                print("Code execution timed out.")
                retry_delay += 0.1  # Increase the retry delay for the next attempt
                driver.quit()
                print("Driver quit.")
                sleep(retry_delay)
                driver = webdriver.Chrome()
                sleep(10)
            except Exception as e:
                print("An error occurred:", e)
                retry_delay += 0.1
                driver = None
                while driver is None:
                    try:
                        driver = webdriver.Chrome()
                    except Exception as chrome_error:
                        print("Failed to create new Chrome driver:", chrome_error)
                        sleep(retry_delay)

            finally:
                # Cancel the timeout alarm
                signal.alarm(0)
                

        #soup = BeautifulSoup(response.text,'html.parser')
        counter +=1
        
        #Guardar informacion del titulo y direccion de la oferta laboral
        #ui-pdp-title
        #item-title__primary
        try:
            titles.append(soup.find('h1',class_='ui-pdp-title').text)
        except (AttributeError,IndexError):
            titles.append(np.nan)
    
        #ui-pdp-color--BLACK ui-pdp-size--SMALL ui-pdp-family--REGULAR ui-pdp-media__title

        #address.append(soup.find('h2',class_='map-address').text)
        try: 
            #father_address_tmp = soup.find('div',class_='ui-pdp-media ui-vip-location__subtitle ui-pdp-color--BLACK')
            #print(father_address_tmp)
            address_tmp = soup.find_all('p',class_='ui-pdp-color--BLACK ui-pdp-size--SMALL ui-pdp-family--REGULAR ui-pdp-media__title')
            #print(address_tmp[-1].text)
            address.append(address_tmp[-1].text)
        except (AttributeError,IndexError):
            address.append(np.nan)
        
        #Guardar informacion de precios 

        # andes-money-amount__fraction
        # price = soup.find_all('span',class_='price-tag-fraction')
        try:
            price = soup.find('span',class_='andes-money-amount__fraction')
            #print(price.text)
            prices.append(price.text)
        except (AttributeError,IndexError):
            prices.append(np.nan)

        #Guardar informacion fecha publicacion oferta de arriendo
        # info
        try: 
            dates = soup.find('p',class_='ui-pdp-color--GRAY ui-pdp-size--XSMALL ui-pdp-family--REGULAR ui-pdp-header__bottom-subtitle')
            #print(dates)
            if dates == None:
                dates = soup.find('p',class_='ui-pdp-color--GRAY ui-pdp-size--XSMALL ui-pdp-family--REGULAR ui-pdp-seller-validated__title')
            #print(dates.text)
            publication_date.append(dates.text)
        except (AttributeError,IndexError):
            publication_date.append(np.nan)


        try:
            desc = soup.find('p',class_='ui-pdp-color--GRAY ui-pdp-size--XSMALL ui-pdp-family--REGULAR ui-pdp-maintenance-fee-ltr').text
            highlighted_common_expenses.append(desc)
        except (AttributeError,IndexError):
            highlighted_common_expenses.append(np.nan)

        try:
            characs = soup.find_all('span',class_='ui-pdp-color--BLACK ui-pdp-size--SMALL ui-pdp-family--REGULAR ui-pdp-label')
            list_characs = ''
            for i in range(len(characs)):
                charac_tmp = characs[i].text
                #print(charac_tmp)
                if i == 0:
                    list_characs = list_characs + charac_tmp
                else:
                    list_characs = list_characs + ' / '+ charac_tmp
            highlighted_characteristics.append(list_characs)
            #print(len(characs))
            number_highlighted_characteristics.append(len(characs))
        except (AttributeError,IndexError):
            highlighted_characteristics.append(np.nan)

        '''
        #Guardar informacion de ambientes, comodidades y otras caracteristicas
        try:
            mood_cons = soup.find_all('ul',class_='attribute-list')
            if len(mood_cons) == 1:
                ambiances.append(mood_cons[0].text)
                amenities.append(np.nan)
                other_features.append(np.nan)

            if len(mood_cons)==2:
                ambiances.append(mood_cons[0].text)
                amenities.append(mood_cons[1].text)
                other_features.append(np.nan)

            if len(mood_cons)==3:
                ambiances.append(mood_cons[0].text)
                amenities.append(mood_cons[1].text)
                other_features.append(mood_cons[2].text)

        except (AttributeError,IndexError):
            ambiances.append(np.nan)
            amenities.append(np.nan)
            other_features.append(np.nan)

        #Guardar info de descripcion
        try:
            desc = soup.find('div',class_='item-description__text').text
            description.append(desc)
        except (AttributeError,IndexError):
            description.append(np.nan)

        try:
            attribute = soup.find('ul',{'class':'specs-list'}).find_all('li')
            
            for a in attribute:
                heading = a.strong.text
                values = a.span.text

                
                if heading == 'Dormitorios':
                    rooms.append(values)
                
                if heading == 'Baños':
                    toilets.append(values)
            
                if heading == 'Superficie total':
                    total_m2.append(values)
                
                if heading == 'Superficie útil':
                    util_m2.append(values)

                if heading =='Estacionamientos':
                    parking.append(values)

                if heading == 'Gastos comunes':
                    common_spends.append(values)

                if heading == 'Bodegas':
                    garage.append(values)
                
                if heading == 'Antigüedad':
                    olds.append(values)
                
                if heading == 'Orientación':
                    orientation.append(values)
                
                if heading == 'Número de piso de la unidad':
                    apartment_floor_number.append(values)
                
                if heading == 'Departamentos por piso':
                    apartments_per_floor.append(values)
                
                if heading == 'Cantidad de pisos':
                    floors_numbers.append(values)
        except (AttributeError,IndexError):

            rooms.append(np.nan)
            toilets.append(np.nan)
            total_m2.append(np.nan)
            util_m2.append(np.nan)
            parking.append(np.nan)
            garage.append(np.nan)
            olds.append(np.nan)
            common_spends.append(np.nan)
            orientation.append(np.nan)
            apartment_floor_number.append(np.nan)
            apartments_per_floor.append(np.nan)
            floors_numbers.append(np.nan)


        '''
        #Clausula para mantener cantidad de variables por cada oferta de departamento, en caso de no existir esa variable se llena con nan
        if len(titles) != counter:
            titles.append(np.nan)
        if len(address) != counter:
            address.append(np.nan)
        if len(publication_date) != counter:
            publication_date.append(np.nan)
        if len(prices) != counter:
            prices.append(np.nan)
        if len(highlighted_common_expenses)!= counter:
            highlighted_common_expenses.append(np.nan)

        if len(highlighted_characteristics)!= counter:
            highlighted_characteristics.append(np.nan)
        if len(number_highlighted_characteristics)!= counter:
            number_highlighted_characteristics.append(np.nan)
            
        '''
        if len(rooms) != counter:
            try:
                rooms.append(soup.find('dd',{'class':'align-room'}).text)
            except (AttributeError,IndexError):
                rooms.append(np.nan)
        
        if len(toilets) != counter:
            try:
                toilets.append(soup.find('dd',{'class':'align-bathroom'}).text)
            except (AttributeError,IndexError):
                toilets.append(np.nan)
       

        if len(util_m2) != counter:
            try:
                util_m2.append(soup.find('dd',{'class':'align-surface'}).text)
            except (AttributeError,IndexError):
                util_m2.append(np.nan)
      
        if len(total_m2) != counter:
            total_m2.append(np.nan)
        if len(parking) != counter:
            parking.append(np.nan)
        if len(garage) != counter:
            garage.append(np.nan)
        if len(olds) != counter:
            olds.append(np.nan)
        if len(common_spends) != counter:
            common_spends.append(np.nan)
        if len(orientation) != counter:
            orientation.append(np.nan)
        if len(apartment_floor_number) != counter:
            apartment_floor_number.append(np.nan)
        if len(apartments_per_floor) != counter:
            apartments_per_floor.append(np.nan)
        if len(floors_numbers) != counter:
            floors_numbers.append(np.nan)
        
        if len(ambiances) != counter:
            ambiances.append(np.nan)
        if len(amenities) != counter:
            amenities.append(np.nan)
        if len(other_features) != counter:
            other_features.append(np.nan)
        '''
        print(f"Departamentos en {scope} encontrados: {len(titles)}")
        clear_output(wait=True)

    print(f"Total informacion extraida de departamentos en {scope}: {len(titles)}")
    print('Web Scraping Completado!\n')

    driver.quit()
    '''
    df = pd.DataFrame({'fecha descarga':date.today(),'fecha publicacion':publication_date,'titulo':titles,'direccion':address,
                    'gastos comunes destacados':highlighted_common_expenses,'caracteristicas destacados':highlighted_characteristics,
                    'descripcion':description,'ambiente':ambiances,'comodidades':amenities,'otras caracteristicas':other_features,
                    'orientacion':orientation,'antiguedad':olds,'m2 totales':total_m2,'m2_utiles':util_m2,'habitaciones':rooms,
                    'banos':toilets,'estacionamiento':parking,'bodega':garage,'piso de apartamento':apartment_floor_number,
                    'cantidad de pisos edificio':floors_numbers,'apartamentos por piso':apartments_per_floor,'gastos comunes': common_spends,
                    'precio':prices,'url':urls})
    '''

    df = pd.DataFrame({'direccion':address,'precio':prices, 
                       'gastos_comunes':highlighted_common_expenses,
                       'caracteristicas':highlighted_characteristics,
                       'num_caracteristicas':number_highlighted_characteristics,                       
                       'fecha_descarga':date.today(),'fecha_publicacion':publication_date,
                       'titulo':titles,'url':urls})
    return df






def look_results_number(region,type,scope,rango_precio):

    init_url = 'https://www.portalinmobiliario.com/'+scope.lower().replace(" ","-")+'/'+type+'/'+region+'/_Desde_'+ str(1)+rango_precio
    print(init_url)
    init_response = requests.get(init_url)
    sleep(0.05)
    init_soup = BeautifulSoup(init_response.text,'html.parser')
    try:
        test_var = (init_soup.find('span',class_='ui-search-search-result__quantity-results shops-custom-secondary-font').text)
        pattern = r"\d{1,3}(?:\.\d{3})*"

        # Find all matches of the pattern in the text string
        matches = re.findall(pattern, test_var)

        # Extract the first match and remove the thousands separators
        clean_number = matches[0].replace(".", "")

    except (AttributeError,IndexError) as e:
        print(e)
        sys.exit(1)

    return clean_number





def webscraping_deptos_all(region,type,scope, rango_precio='_PriceRange_0CLP-0CLP'):  
    dfs = []
    current_rango_precio = rango_precio
    prices_used_list=[]

    pattern = r"(\d+)CLP-(\d+)CLP"

    # Find all matches of the pattern in the text string
    matches = re.findall(pattern, current_rango_precio)

    # Extract the second-to-last match and convert it to integers
    number1 = int(matches[0][0])
    number2 = int(matches[0][1])

    while True:
        clean_number  = look_results_number(region,type,scope,current_rango_precio)
        if int(clean_number) ==0:
            break
        if int(clean_number)> 2000 and number2==0:
            number2 = number1+500000
            current_rango_precio = '_PriceRange_'+str(number1)+'CLP-'+str(number2)+'CLP'
        while int(clean_number)> 2000:
            # Define a regular expression pattern to match the number segment
            pattern = r"(\d+)CLP-(\d+)CLP"

            # Find all matches of the pattern in the text string
            matches = re.findall(pattern, current_rango_precio)

            # Extract the second-to-last match and convert it to integers
            number1 = int(matches[0][0])
            number2 = int(matches[0][1])

            # Modify the first number as desired
            number2 = number2 - int((number2-number1)/4)  

            # Construct the new text with the modified number
            current_rango_precio = re.sub(pattern, str(number1) + "CLP-" + str(number2) + "CLP", current_rango_precio, count=1)
            clean_number  = look_results_number(region,type,scope,current_rango_precio)

        #print(current_rango_precio)
        prices_used_list.append(current_rango_precio)
        # Open a file in write mode
        with open("prices_used_list.txt", "w") as file:
            # Write each list element to a new line in the file
            for item in prices_used_list:
                file.write(str(item) + "\n")
        df = webscraping_deptos(region, 40, type, scope, current_rango_precio)
        # Append the data frame to the list

        now = datetime.now()
        formatted_time = now.strftime("%Y-%m-%d %H-%M-%S")

        df.to_csv('./data/'+'all-data-raw-from-'+region+'_'+formatted_time+'_'+current_rango_precio+'_'+'.csv',index=False)
        dfs.append(df)
        if int(number2) == 0:
            break
        number1 = number2+1
        number2 = 0
        current_rango_precio = '_PriceRange_'+str(number1)+'CLP-'+str(number2)+'CLP'

    # Concatenate vertically
    concatenated_df = pd.concat(dfs, axis=0)
    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H-%M-%S")

    concatenated_df.to_csv('./data/'+'all-data-raw-from-'+region+'_'+formatted_time+'_concatenated_'+'.csv',index=False)
    
    return concatenated_df