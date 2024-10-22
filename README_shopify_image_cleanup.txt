
# Shopify Duplicate Image Removal Script

This Python script identifies and deletes duplicate images from Shopify products based on file size. It is optimized to process products within a specific collection, removing unnecessary duplicate images and reducing storage usage.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Shopify Setup](#shopify-setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [Final Report](#final-report)

## Features

- Deletes duplicate product images based on file size.
- Processes only products within a specified Shopify collection.
- Provides a final report showing the total number of files deleted and the total file size reduced.

## Requirements

- Python 3.x
- A Shopify store
- A Shopify custom app with API access

## Installation

### Step 1: Clone the Repository


git clone https://github.com/yourusername/shopify-duplicate-image-removal.git
cd shopify-duplicate-image-removal


### Step 2: Install Python Libraries

You will need to install the required Python libraries. Run the following command:

pip install requests


## Shopify Setup

### Step 1: Create a Custom Shopify App

1. Log in to your Shopify admin panel.
2. Navigate to **Apps** > **Develop apps**.
3. Click on **Create an app** and give your app a name.
4. In the **App Setup**, under **Admin API Access Scopes**, assign the following scopes:
-read_files
-write_files
-write_products
-read_products
-write_product_listings
-read_product_listings
-write_product_feeds
-read_product_feeds
5. Click **Save**.
6. Install the app to your Shopify store by clicking **Install app**.
7. After installation, you’ll be given an **API Access Token**. **Save this token** — you’ll need it to configure the script.

### Step 2: Find the Collection ID

To process products in a specific collection, you need to know the collection ID.

1. Go to **Products** > **Collections** in your Shopify admin.
2. Click on the collection you want to process.
3. The URL in your browser will look something like this:
   ```
   https://yourstore.myshopify.com/admin/collections/1234567890
   ```
   The number `1234567890` is the **Collection ID**.

## Configuration

1. Open the Python script in a text editor.
2. Replace the following placeholder values:
   - `ACCESS_TOKEN = "your_access_token_here"` with your **API Access Token** from Shopify.
   - `COLLECTION_ID = "your_collection_id_here"` with the ID of the collection you want to process.
3. Set the store name:
   ```python
   STORE_NAME = "yourstore"  # Replace with your Shopify store's subdomain
   ```

## Usage

To run the script:

1. Open a terminal or command prompt.
2. Navigate to the script's directory.
3. Run the script using Python:

```bash
python shopify_image_cleanup.py
```

The script will:
- Fetch all products from the specified collection.
- Check for duplicate images based on file size.
- Delete duplicate images.
- Display progress in the terminal.

## Final Report

At the end of the script execution, a summary will be provided, including:
- **Total files deleted**
- **Total file size reduced** (in MB)

---

### Example Final Report:

```
Final Report:
Total files deleted: 20
Total file size reduced: 15.32 MB
```

---

## Notes

- Make sure your API token is kept private and secure. **Do not commit it** to version control.
- You can adjust the `PRODUCTS_PER_PAGE` variable if you want to fetch more or fewer products per page.

## License

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International License**. See the [LICENSE](LICENSE) file for details.

