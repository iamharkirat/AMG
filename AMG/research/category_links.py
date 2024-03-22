from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def create_chrome_driver():
    print("begin create chrome drive")
    driver_path = ChromeDriverManager().install()
    service = Service(driver_path)
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()
    return driver


def main():
    driver = create_chrome_driver()
    link = 'https://amgmedical.com/shop-products/'
    driver.get(link)

    print("WebDriver has navigated to the shop products page.")

    # Wait for the navList element to be present
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'navList'))
    )

    print("navList element is present on the page.")

    # Find the navList element
    nav_list = driver.find_element(By.CLASS_NAME, 'navList')

    # Find all navList-items
    nav_list_items = nav_list.find_elements(By.CLASS_NAME, 'navList-item')

    print(f"Found {len(nav_list_items)} navList items.")

    # Extract and print href links
    href_links = []
    for nav_list_item in nav_list_items:
        href_element = nav_list_item.find_element(By.CSS_SELECTOR, 'a')
        href_link = href_element.get_attribute('href')
        href_links.append(href_link)
        print(f"Extracted href link: {href_link}")

    # Modify href links with page numbers and save to a file
    file_path = 'artifacts/main_category_links.txt'
    with open(file_path, 'w') as file:
        for href_link in href_links:
            file.write(f"{href_link}\n")
            for page_number in range(2, 12):
                file.write(f"{href_link.rstrip('/')}/?page={page_number}\n")

    print(f"Scraper has finished extracting href links and saved to {file_path}.")

    # Close the WebDriver when done
    driver.quit()

    print("WebDriver has been closed.")

if __name__ == '__main__':
    main()
