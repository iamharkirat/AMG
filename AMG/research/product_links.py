import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

def create_chrome_driver():
    print("begin create chrome drive")
    driver_path = ChromeDriverManager().install()
    service = Service(driver_path)
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()
    return driver

def extract_product_links(driver, category_url):
    driver.get(category_url)

    # Set a global timeout for the WebDriver to wait for elements
    driver.implicitly_wait(10)

    try:
        product_grid = driver.find_element(By.CLASS_NAME, 'productGrid')
        products = product_grid.find_elements(By.CLASS_NAME, 'product')
    except NoSuchElementException:
        print(f"No products found for category: {category_url}")
        return []

    print(f"Found {len(products)} products on this page.")

    product_links = []

    for product in products:
        href_element = product.find_element(By.CSS_SELECTOR, 'a')
        href_link = href_element.get_attribute('href')
        print(f"Extracted product link: {href_link}")
        product_links.append(href_link)

    return product_links

# Update the main function
def main():
    driver = create_chrome_driver()
    main_category_links_file = 'artifacts/main_category_links.txt'

    with open(main_category_links_file, 'r') as category_file:
        categories = category_file.read().splitlines()

    for category_url in categories:
        print(f"\nProcessing category: {category_url}")
        product_links = extract_product_links(driver, category_url)

        # Save product links to a file
        if product_links:
            product_links_file = 'artifacts/product_links.txt'
            with open(product_links_file, 'a') as file:
                for link in product_links:
                    file.write(f"{link}\n")

    # Allow time for the page to load before quitting the WebDriver
    time.sleep(2)

    # Close the WebDriver when done
    driver.quit()
    print("WebDriver has been closed.")

if __name__ == '__main__':
    main()
