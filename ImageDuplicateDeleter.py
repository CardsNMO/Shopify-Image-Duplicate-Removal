import requests
import time

# Shopify Admin API Access Token
ACCESS_TOKEN = "INSERT YOUR API ACCESS TOKEN HERE"  # Replace with your Admin API Access Token
STORE_NAME = "STORE #"  # Replace with your store number found on your shopify admin url
API_VERSION = "2024-10"
PRODUCTS_PER_PAGE = 250  # Shopify allows a maximum of 250 products per page

# Collection ID for the specific collection you want to process
COLLECTION_ID = "COLLECTION NUMBER"  # Replace with your actual collection ID

# Base URL for Shopify API
BASE_URL = f"https://{STORE_NAME}.myshopify.com/admin/api/{API_VERSION}"

# Variables to track total deletions and file size reduction
total_files_deleted = 0
total_file_size_reduced = 0  # In bytes

# Retry logic function
def request_with_retries(url, headers, method='get', retries=3, timeout=30):
    for i in range(retries):
        try:
            if method == 'get':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'delete':
                response = requests.delete(url, headers=headers, timeout=timeout)
            elif method == 'head':
                response = requests.head(url, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                return response  # Success, return response
            else:
                print(f"Error: Received status code {response.status_code} for URL: {url}")
                return None
        except requests.exceptions.Timeout:
            print(f"Timeout occurred, retrying ({i + 1}/{retries})...")
            time.sleep(2)  # Wait before retrying
    print("Failed after retries.")
    return None

# Function to check rate limits
def check_rate_limit(response):
    if 'X-Shopify-Shop-Api-Call-Limit' in response.headers:
        call_limit = response.headers['X-Shopify-Shop-Api-Call-Limit']
        used, limit = map(int, call_limit.split('/'))
        if used >= 35:  # Pause when 35 or more requests have been made
            print(f"Rate limit nearing: {used}/{limit}. Pausing for 5 seconds...")
            time.sleep(5)  # Pause for 5 seconds to avoid hitting the rate limit

# Function to get and process products from a specific collection using cursor-based pagination
def get_and_process_products_in_collection():
    processed_products = 0
    next_page_info = None

    while True:
        print("Fetching products from collection...")  # Track progress
        if next_page_info:
            url = f"{BASE_URL}/collections/{COLLECTION_ID}/products.json?limit={PRODUCTS_PER_PAGE}&page_info={next_page_info}"
        else:
            url = f"{BASE_URL}/collections/{COLLECTION_ID}/products.json?limit={PRODUCTS_PER_PAGE}"

        headers = {
            "X-Shopify-Access-Token": ACCESS_TOKEN
        }

        response = request_with_retries(url, headers=headers, timeout=30)
        if response and response.status_code == 200:
            check_rate_limit(response)  # Check rate limits after each request
            data = response.json()
            products = data['products']

            # Process products that have more than one image
            for product in products:
                product_id = product['id']
                product_title = product['title']
                num_images = len(product['images'])  # Count of images

                if num_images > 1:
                    print(f"Processing product {product_id}: {product_title} (Images: {num_images})")
                    remove_duplicate_images(product_id)
                else:
                    print(f"Skipping product {product_id}: {product_title} (Images: {num_images})")
                
                processed_products += 1  # Increment processed products

            # Check if there is a next page (pagination)
            if 'Link' in response.headers:
                # Look for the 'rel="next"' link
                links = response.headers['Link'].split(',')
                for link in links:
                    if 'rel="next"' in link:
                        # Extract the page_info parameter
                        next_page_info = link.split('page_info=')[1].split('>')[0]
                        print(f"Next page info: {next_page_info}")
                        break
                else:
                    # No next page found, stop the loop
                    print("No more pages.")
                    break
            else:
                print("No pagination link found.")
                break
        else:
            print(f"Error retrieving products from collection")
            break

# Function to get the file size of an image using a HEAD request
def get_image_file_size(image_url):
    response = request_with_retries(image_url, headers={}, method='head', timeout=30)
    if response and response.status_code == 200:
        return int(response.headers.get('Content-Length', 0))  # Return file size in bytes
    else:
        print(f"Error retrieving file size for image: {image_url}")
        return 0

# Function to delete an image by image_id and track deleted file sizes
def delete_image(product_id, image_id, image_src, file_size):
    global total_files_deleted, total_file_size_reduced
    url = f"{BASE_URL}/products/{product_id}/images/{image_id}.json"
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN
    }
    response = request_with_retries(url, headers=headers, method='delete', timeout=30)
    check_rate_limit(response)  # Check rate limits after each request

    if response and response.status_code == 200:
        print(f"Deleted image with ID {image_id} from product {product_id} (source: {image_src})")
        total_files_deleted += 1
        total_file_size_reduced += file_size  # Accumulate file size reduction
    else:
        print(f"Error deleting image {image_id} from product {product_id}")

# Function to identify and delete duplicate images for a product
def remove_duplicate_images(product_id):
    images = get_product_images(product_id)
    image_file_sizes = {}  # Dictionary to track file sizes

    for image in images:
        image_id = image['id']
        image_src = image['src']  # Get the image source URL

        # Fetch the actual file size of the image using a HEAD request
        file_size = get_image_file_size(image_src)

        # If file size already exists in the dictionary, it's a duplicate
        if file_size in image_file_sizes:
            print(f"Duplicate found for image ID {image_id} in product {product_id} (file size {file_size} bytes)")
            delete_image(product_id, image_id, image_src, file_size)  # Pass file size for tracking
        else:
            # Add new image file size to dictionary
            image_file_sizes[file_size] = image_id

# Function to get product images
def get_product_images(product_id):
    url = f"{BASE_URL}/products/{product_id}/images.json"
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN
    }
    response = request_with_retries(url, headers=headers, timeout=30)
    check_rate_limit(response)  # Check rate limits after each request

    if response and response.status_code == 200:
        return response.json()['images']
    else:
        print(f"Error retrieving images for product {product_id}")
        return []


# Start the process
get_and_process_products_in_collection()

# Display the final report
print(f"\nFinal Report:")
print(f"Total files deleted: {total_files_deleted}")
print(f"Total file size reduced: {total_file_size_reduced / (1024 * 1024):.2f} MB")  # Convert bytes to MB
