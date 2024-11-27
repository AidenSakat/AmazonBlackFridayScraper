from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Works for black friday page and daily deals page
url = "https://www.amazon.com/blackfriday"
chrome_options = Options()
chrome_options.add_experimental_option("detach", True);
driver = webdriver.Chrome(options=chrome_options)
driver.get(url)

product_list = []
visited_links = set()

def scroll_down(driver):
    # Scroll down by a portion of the page
    scroll_height = driver.execute_script("return document.documentElement.scrollHeight;")
    current_position = driver.execute_script("return window.pageYOffset;")
    new_position = current_position + (scroll_height / 8)
    
    driver.execute_script(f"window.scrollTo(0, {new_position});")
    time.sleep(1)  # Add a delay to allow the page to load the content

def fetch_products(product):
    # Extract product details
    product_link = product.find_element(By.CSS_SELECTOR, "a").get_attribute("href")

    if product_link in visited_links:
        return
    
    visited_links.add(product_link)
    driver.execute_script("window.open(arguments[0]);", product_link)
    driver.switch_to.window(driver.window_handles[-1])
    
    # Wait until product title is available (once available, all other elements should be as well)
    try:
        product_name = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, './/*[@id="productTitle"]'))
        ).text
    except:
        product_name = 'N/A'
    
    # Get product price
    try:
        product_price = driver.find_element(By.XPATH, './/*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[3]/span[2]/span[2]').text
    except:
        product_price = 'N/A'
        try:
            product_price = driver.find_element(By.XPATH, './/*[@id="corePrice_desktop"]/div/table/tbody/tr/td[2]/span[1]').text
        except:
            product_price = 'N/A'
    
    # Get original price
    try:
        original_price = driver.find_element(By.XPATH, './/*[@id="corePriceDisplay_desktop_feature_div"]/div[2]/span/span[1]/span[2]/span').text
    except:
        original_price = 'N/A'

    # Get clip coupon if available
    try:
        clip_coupon = driver.find_element(By.XPATH, './/*[@id="promoPriceBlockMessage_feature_div"]').text
    except:
        clip_coupon = 'N/A'
    # get the discount %
    try:
      discount = driver.find_element(By.XPATH, './/*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[2]').text
    except:
      discount = 'N/A'
    # Print product details
    print(f"Product: {product_name}")
    print(f"Price: ${original_price}")
    print(f"Discounted Price: ${product_price}")
    print(f"Coupon: {clip_coupon}")
    print(f"Discout: {discount}")

    # Close the product page and switch back to the main page
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    # Append product details to the list
    product_item = {
        'product_name': product_name,
        'product_price': product_price,
        'original_price': original_price,
        'discount' : discount,
        'clip_coupon': clip_coupon,
        'Product_link' : product_link,
    }
    
    product_list.append(product_item)

products_to_scrape = 5 # adjust this for how many products to scrape
while len(product_list) < products_to_scrape:
    # Find all product elements
    products = driver.find_elements(By.CLASS_NAME, "GridItem-module__container_PW2gdkwTj1GQzdwJjejN")

    if not products:  # Stop if no products are found
        break

    # Fetch details for each product then breaks if requested amount is reached
    for product in products:
        if len(product_list) >= products_to_scrape:
            break

        fetch_products(product)

    # Scroll down to load more products
    scroll_down(driver)

# Saves the data into a viewable excel sheet
df = pd.DataFrame(product_list)
df.to_excel('amazon_products.xlsx', index=True)

driver.quit()
