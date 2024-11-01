import requests
import json
import pandas as pd
from bs4 import BeautifulSoup

def fetch_json_from_url(url_or_urls):
    """
    Fetches JSON data from a single URL or a list of URLs.

    Parameters:
        url_or_urls (str or list of str): A single URL or a list of URLs to fetch JSON data from.

    Returns:
        list of dict: A list of JSON objects retrieved from the provided URL(s).
    """
    if isinstance(url_or_urls, str):
        url_or_urls = [url_or_urls]
    
    json_objects = []
    
    for url in url_or_urls:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            json_objects.append(response.json())
        except requests.exceptions.RequestException as e:
            print(f"Request to {url} failed: {e}")
    
    return json_objects

def col_get_dept_codes():
    json_data = fetch_json_from_url("https://www.datos.gov.co/resource/82di-kkh9.json?$limit=12000&$select=distinct dpto, cod_depto")
    # Flattening  and filteringthe JSON data
    flattened_data = [item for sublist in json_data for item in sublist]
    # Filtering
    filtered_data = [item for item in flattened_data if 'dpto' in item]
    # Creating a DataFrame
    df = pd.DataFrame(filtered_data).sort_values(by='cod_depto').reset_index(drop=True)
    return df

def col_get_municipios_by_dept_name(dept:str):
    dept = dept.upper()
    json_data = fetch_json_from_url(f"https://www.datos.gov.co/resource/82di-kkh9.json?$limit=12000&dpto={dept}")
    # Flattening  and filteringthe JSON data
    flattened_data = [item for sublist in json_data for item in sublist]
    # Filtering
    filtered_data = [item for item in flattened_data if 'dpto' in item]
    # Creating a DataFrame
    df = pd.DataFrame(filtered_data).sort_values(by='cod_mpio').reset_index(drop=True).loc[:,["cod_mpio", "nom_mpio"]]
    return df

def col_get_all_municipios():
    json_data = fetch_json_from_url(f"https://www.datos.gov.co/resource/82di-kkh9.json?$limit=12000")
    # Flattening  and filteringthe JSON data
    flattened_data = [item for sublist in json_data for item in sublist]
    # Filtering
    filtered_data = [item for item in flattened_data if 'dpto' in item]
    # Creating a DataFrame
    df = pd.DataFrame(filtered_data).sort_values(by='cod_mpio').reset_index(drop=True).loc[:,["cod_mpio", "nom_mpio"]]
    return df

def br_get_dept_codes():
    url = 'https://www.ibge.gov.br/explica/codigos-dos-municipios.php'
     # Fetch the content of the URL
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
        return None
    rows = BeautifulSoup(response.text, 'html.parser').find('table', class_='container-uf').find('tbody', class_='codigos-list').find_all('tr')
    pre_df=[]
    for row in rows:
        cells = row.find_all(['td', 'th'])
        pre_row =[]
        for cell in cells:
            value = cell.get_text(strip=True)
            if "ver" in value:
                value = value[:2]
            pre_row.append(value)
        pre_df.append(pre_row)
    return pd.DataFrame(pre_df, columns=['ufs', 'code'])

def br_get_municipios_by_dept_name(dpto):
    url = 'https://www.ibge.gov.br/explica/codigos-dos-municipios.php'
     # Fetch the content of the URL
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find the table with class 'container-uf'
    tables = soup.find_all('table', class_='container-uf')
    if not tables:
        print("Table with class 'container-uf' not found.")
        return
    for table in tables:
        if table.find('th').get_text()[14:].lower() == dpto.lower():
            rows = table.find('tbody', class_='codigos-list').find_all('tr')
            pre_df=[]
            for row in rows:
                cells = row.find_all(['td', 'th'])
                pre_row =[]
                for cell in cells:
                    value = cell.get_text(strip=True)
                    if "ver" in value:
                        value = value[:2]
                    pre_row.append(value)
                pre_df.append(pre_row)
            return pd.DataFrame(pre_df, columns=['municipio', 'code'])

def br_get_all_municipios():
    url = 'https://www.ibge.gov.br/explica/codigos-dos-municipios.php'
     # Fetch the content of the URL
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find the table with class 'container-uf'
    tables = soup.find_all('table', class_='container-uf')
    if not tables:
        print("Table with class 'container-uf' not found.")
        return
    pre_df=[]
    for i in range(len(tables)):
        if i == 0:
            continue
        rows = tables[i].find('tbody', class_='codigos-list').find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            pre_row =[]
            for cell in cells:
                value = cell.get_text(strip=True)
                if "ver" in value:
                    value = value[:2]
                pre_row.append(value)
            pre_df.append(pre_row)
    return pd.DataFrame(pre_df, columns=['municipio', 'code'])


print(br_get_all_municipios())
print(col_get_all_municipios())
breakpoint()
print(col_get_dept_codes())
print(col_get_municipios_by_dept_name("ANTIOQUIA"))
print(col_get_all_municipios())
print(br_get_dept_codes())
print(br_get_municipios_by_dept_name("Paraná"))