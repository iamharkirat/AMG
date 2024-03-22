import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def create_chrome_driver():
    print("Initializing Chrome WebDriver...")
    driver_path = ChromeDriverManager().install()
    service = Service(driver_path)
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()
    print("Chrome WebDriver initialized.")
    return driver

def get_product_info(driver):
    # Product Name
    product_name = driver.find_element(By.CSS_SELECTOR, '.productView-title').text

    # Product Category
    breadcrumbs = driver.find_elements(By.CSS_SELECTOR, '.breadcrumbs li')
    product_category = breadcrumbs[2].find_element(By.CSS_SELECTOR, '.breadcrumb-label').text

    # SKU ID
    sku_id = driver.find_element(By.CSS_SELECTOR, '.productView-info-value').text

    return product_name, product_category, sku_id

def get_msrp(driver):
    time.sleep(3)  # Wait for 3-4 seconds for the MSRP to load
    msrp_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.price--withoutTax')))
    return msrp_element.text

def select_all_combinations(driver, url):
    dropdowns = driver.find_elements(By.CSS_SELECTOR, '.productView-options-inner .form-field')
    # Extract options and labels from each dropdown
    dropdown_options = {}
    labels = []
    for dropdown in dropdowns:
        label = dropdown.find_element(By.CSS_SELECTOR, 'label').text.split(':')[0]  # Getting label text before colon
        select_element = dropdown.find_element(By.TAG_NAME, 'select')
        options = [option.text for option in select_element.find_elements(By.TAG_NAME, 'option')]
        dropdown_options[label] = options
        labels.append(label)

    # Initialize dictionary to store data
    data = {label: [] for label in labels}
    data['MSRP'] = []
    data['Product Name'] = []
    data['Product Category'] = []
    data['SKU ID'] = []
    data['URL'] = []  # Add URL to the data dictionary

    # Get product info
    product_name, product_category, sku_id = get_product_info(driver)

    # Generate all combinations of options
    from itertools import product
    all_combinations = product(*dropdown_options.values())

    for combination in all_combinations:
        # Select options from dropdowns
        for dropdown, option in zip(dropdowns, combination):
            select_element = dropdown.find_element(By.TAG_NAME, 'select')
            Select(select_element).select_by_visible_text(option)

        # Get updated MSRP
        msrp = get_msrp(driver)

        # Store values in lists
        data['MSRP'].append(msrp)
        for label, option in zip(labels, combination):
            data[label].append(option)
        data['Product Name'].append(product_name)
        data['Product Category'].append(product_category)
        data['SKU ID'].append(sku_id)
        data['URL'].append(url)  # Store the URL for each product combination

    # Create DataFrame
    df = pd.DataFrame(data)

    return df

def merge_product_dataframes(df_list):
    combined_df = pd.DataFrame()
    for df in df_list:
        if combined_df.empty:
            combined_df = df
        else:
            # Add new columns with "N/A" as default values
            for column in set(df.columns) - set(combined_df.columns):
                combined_df[column] = "N/A"
            # Align current df to combined_df's columns, adding "N/A" for missing ones
            df = df.reindex(columns=combined_df.columns, fill_value="N/A")
            combined_df = pd.concat([combined_df, df], ignore_index=True)
    return combined_df

def main():
    # Path to the file containing product URLs
    links_file_path = 'AMG/artifacts/product_links.txt'
    
    # Read product URLs from file
    with open(links_file_path, 'r') as file:
        product_urls = [line.strip() for line in file.readlines() if line.strip()]
    
    all_dfs = []
    driver = create_chrome_driver()
    
    for url in product_urls:
        try:
            driver.get(url)
            product_df = select_all_combinations(driver, url)  # Pass the current URL
            all_dfs.append(product_df)
        except Exception as e:
            print(f"Failed to process {url}: {e}")

    driver.quit()

    # Merge all product DataFrames into a single DataFrame
    combined_df = merge_product_dataframes(all_dfs)
    
    # Save the combined DataFrame as an Excel file in the artifacts folder
    excel_file_path = 'artifacts/combined_product_data.xlsx'
    combined_df.to_excel(excel_file_path, index=False)

if __name__ == "__main__":
    main()


# https://amgmedical.com/shop-products/clearance/amg-foerster-forceps/
