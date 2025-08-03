"""
Skincare Product Scraper for Snapklik.com

This script scrapes skincare product data from Snapklik.com and groups products by similar key ingredients.
It extracts product information and categorizes them based on their ingredients or product categories.

Features:
- Extracts product data including name, brand, price, ingredients, etc.
- Groups products by similar key ingredients using heuristic analysis
- Creates a grouped output table showing top products for each ingredient category
- Handles both API and HTML parsing fallback methods
"""

import time
import re
import pandas as pd
import requests
import json
import os
from collections import defaultdict

def fetch_products_from_api(page=0, search_term="skin care"):

    url = f"https://sk-backend-xxhrslt5oq-uc.a.run.app/a/sr/?p={page}&s={search_term}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://snapklik.com",
        "Referer": "https://snapklik.com/"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching products from API: {e}")
        # Try to parse HTML as fallback
        try:
            if not os.path.exists('debug.html'):
                print("Warning: debug.html file not found for fallback parsing")
                return None
            
            with open('debug.html', 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            import re
            import json
            product_objects = []
            # Use a more specific regex pattern to match complete product objects
            product_pattern = r'\{[^{]*"skid":"[^"]*"[^}]*"categories":\[[^\]]*\][^}]*\}'
            matches = re.findall(product_pattern, html_content)
            
            for match in matches:
                try:
                    data = json.loads(match)
                    # Check if it has the required fields
                    if 'skid' in data and 'categories' in data:
                        product_objects.append(data)
                except Exception:
                    # Try to extract partial data using regex patterns
                    try:
                        # Look for all available fields
                        skid_match = re.search(r'"skid":"([^"]+)"', match)
                        text_match = re.search(r'"text":"([^"]+)"', match)
                        categories_match = re.search(r'"categories":(\[[^\]]*\])', match)
                        brand_match = re.search(r'"brand":"([^"]*)"', match)
                        price_match = re.search(r'"price":([0-9]+)', match)
                        list_price_match = re.search(r'"listPrice":([0-9]+)', match)
                        score_match = re.search(r'"score":([0-9]+)', match)
                        image_match = re.search(r'"image":"([^"]*)"', match)
                        slug_match = re.search(r'"slug":"([^"]*)"', match)
                        badge_match = re.search(r'"badge":"([^"]*)"', match)
                        rank_name_match = re.search(r'"rankName":"([^"]*)"', match)
                        option_map_match = re.search(r'"OptionMap":(\{[^}]*\})', match)
                        
                        if skid_match and text_match and categories_match:
                            product_data = {
                                "skid": skid_match.group(1),
                                "text": text_match.group(1),
                                "categories": json.loads(categories_match.group(1)),
                                "brand": brand_match.group(1) if brand_match else "",
                                "price": int(price_match.group(1)) if price_match else "",
                                "listPrice": int(list_price_match.group(1)) if list_price_match else "",
                                "score": int(score_match.group(1)) if score_match else "",
                                "image": image_match.group(1) if image_match else "",
                                "slug": slug_match.group(1) if slug_match else "",
                                "badge": badge_match.group(1) if badge_match else "",
                                "rankName": rank_name_match.group(1) if rank_name_match else "",
                                "OptionMap": json.loads(option_map_match.group(1)) if option_map_match else {}
                            }
                            product_objects.append(product_data)
                        elif skid_match and categories_match:
                            # Fallback with minimal required fields
                            product_data = {
                                "skid": skid_match.group(1),
                                "text": text_match.group(1) if text_match else "",
                                "categories": json.loads(categories_match.group(1)),
                                "brand": brand_match.group(1) if brand_match else ""
                            }
                            product_objects.append(product_data)
                    except Exception:
                        continue
                
            # If we didn't find any products with the regex, try a simpler approach
            if not product_objects:
                # Try to find individual product components
                skid_matches = re.findall(r'"skid":"([^"]+)"', html_content)
                text_matches = re.findall(r'"text":"([^"]+)"', html_content)
                categories_matches = re.findall(r'"categories":(\[[^\]]*\])', html_content)
                brand_matches = re.findall(r'"brand":"([^"]*)"', html_content)
                
                # Create product objects from separate matches
                for i in range(min(len(skid_matches), len(text_matches), len(categories_matches))):
                    try:
                        product_data = {
                            "skid": skid_matches[i],
                            "text": text_matches[i],
                            "categories": json.loads(categories_matches[i]),
                            "brand": brand_matches[i] if i < len(brand_matches) else ""
                        }
                        product_objects.append(product_data)
                    except:
                        continue
                
            if product_objects:
                return {
                    "data": {
                        "hits": product_objects,
                        "isFinished": True
                    }
                }
            else:
                # Try another pattern for the data structure
                skid_matches = re.findall(r'"skid":"([^"]+)"', html_content)
                text_matches = re.findall(r'"text":"([^"]+)"', html_content)
                if skid_matches and text_matches:
                    # Create product objects from separate matches
                    hits = []
                    for i in range(min(len(skid_matches), len(text_matches))):
                        hits.append({
                            "skid": skid_matches[i],
                            "text": text_matches[i]
                        })
                    return {
                        "data": {
                            "hits": hits,
                            "isFinished": True
                        }
                    }
        except Exception as html_error:
            print(f"Error parsing HTML: {html_error}")
        return None

def extract_ingredients_from_categories(categories):
    """
    Extract potential key ingredients from product categories using heuristic approach
    
    Since actual ingredients are not directly available in the product data,
    this function uses a heuristic approach to extract potential key ingredients
    from product categories and descriptions.
    
    Args:
        categories (list): List of product categories
    
    Returns:
        list: List of potential key ingredients extracted from categories
    """
    ingredient_keywords = {
        # Acids
        "glycolic", "salicylic", "hyaluronic", "niacinamide", "retinol", "vitamin c",
        "lactic", "mandelic", "azelaic", "kojic", "ferulic", "ascorbic",
        # Botanicals/Extracts
        "aloe", "snail", "witch hazel", "green tea", "chamomile", "calendula",
        "rosehip", "jojoba", "argan", "coconut", "shea", "cucumber",
        # Other actives
        "ceramide", "peptide", "collagen", "caffeine", "zinc", "copper",
        "squalane", "niacinamide", "tocopherol", "retinoid"
    }
    
    # Common product types that indicate ingredients
    product_type_indicators = {
        "serum": "treatment serum",
        "toner": "facial toner",
        "cleanser": "facial cleanser",
        "moisturizer": "face moisturizer",
        "mask": "face mask",
        "scrub": "exfoliating scrub",
        "oil": "facial oil",
        "essence": "skin essence"
    }
    
    # Combine categories into a single string for easier searching
    category_text = " ".join(categories).lower()
    
    # Extract potential ingredients from category text
    found_ingredients = []
    
    # Check for explicit ingredient keywords
    for keyword in ingredient_keywords:
        if keyword in category_text:
            found_ingredients.append(keyword.title())
    
    # Check for product type indicators
    for indicator, description in product_type_indicators.items():
        if indicator in category_text:
            found_ingredients.append(description)
    
    # Add category-based ingredients (last category is often the most specific)
    if categories:
        last_category = categories[-1]
        # Remove generic terms
        if last_category.lower() not in ["skin care", "face", "body", "beauty & personal care"]:
            found_ingredients.append(last_category)
    
    return found_ingredients

def extract_product_data(product):
    """
    Extract relevant data from a product object
    
    This function extracts all relevant product information from a product object
    and structures it in a consistent format for CSV output.
    
    Args:
        product (dict): Product data object
    
    Returns:
        dict: Structured product data with all relevant fields
    """
    product_data = {}
    
    # Basic product information
    product_data["Product Name"] = product.get("text", product.get("name", ""))
    product_data["Brand Name"] = product.get("brand", "")
    product_data["Product Description"] = product.get("description", "")
    product_data["Price"] = product.get("price", "")
    product_data["List Price"] = product.get("listPrice", "")
    product_data["Score"] = product.get("score", "")
    
    # Image
    product_data["Product Images"] = product.get("image", product.get("images", ""))
    
    # Product ID
    product_data["Product ID"] = product.get("skid", product.get("id", ""))
    
    # Source URL
    slug = product.get("slug", "")
    skid = product.get("skid", product.get("id", ""))
    product_data["Source URL"] = f"https://snapklik.com/en-gb/product/{slug}/{skid}" if slug and skid else ""
    
    # Badge and Rank information
    product_data["Badge"] = product.get("badge", "")
    product_data["Rank Name"] = product.get("rankName", "")
    
    # Extract ingredients from categories using heuristic approach
    # Handle different possible structures for categories
    categories = product.get("categories", [])
    if isinstance(categories, str):
        # If categories is a string, try to parse it
        try:
            categories = json.loads(categories)
        except:
            categories = [categories]
    elif not isinstance(categories, list):
        categories = []
    
    # If categories is empty, try to extract from the raw product data
    if not categories:
        # Try to find categories in the raw product data
        for key, value in product.items():
            if "categories" in key.lower() and isinstance(value, str):
                try:
                    categories = json.loads(value)
                    break
                except:
                    if isinstance(value, str):
                        categories = [value]
                        break
    
    ingredients_list = extract_ingredients_from_categories(categories)
    
    # If we couldn't extract specific ingredients, use categories as fallback
    if not ingredients_list:
        # Use the most specific categories (excluding generic ones)
        specific_categories = [cat for cat in categories
                               if cat and cat.lower() not in ["beauty & personal care", "skin care", "face", "body", "eyes"]]
        ingredients_list = specific_categories if specific_categories else categories
    
    product_data["Ingredients"] = " | ".join(ingredients_list) if ingredients_list else ""
    
    # Size/Volume (try to extract from title or option map)
    title = product_data["Product Name"]
    option_map = product.get("OptionMap", product.get("options", {}))
    size_info = ""
    
    # Check option map for size information
    for key, value in option_map.items():
        if "size" in key.lower() or "size" in str(value).lower():
            size_info = str(value)
            break
    
    # If not found in option map, try to extract from title
    if not size_info:
        size_match = re.search(r"\b(\d+\.?\d*\s*(ml|g|oz|fl\s?oz|count|pack))\b", title, re.I)
        size_info = size_match.group(0) if size_match else ""
    
    product_data["Size/Volume"] = size_info
    
    # Skin Concern (try extracting from categories)
    concerns = []
    for category in categories:
        category_lower = category.lower()
        for concern in ["acne", "dark spots", "hyperpigmentation", "wrinkle", "dryness", "sensitivity", "blemish", "pore", "anti-aging", "hydrating"]:
            if concern in category_lower:
                concerns.append(concern)
    product_data["Skin Concern"] = " | ".join(concerns)
    
    # Product Line Name (optional)
    product_data["Product Line Name"] = product.get("line", "")
    
    # Barcode (EAN/UPC)
    product_data["Barcode (EAN/UPC)"] = product.get("barcode", "")
    
    return product_data

def normalize_ingredient(ingredient):
    """
    Normalize ingredient names by removing extra information and standardizing format
    
    This function cleans ingredient names by removing quantities, concentrations,
    and other extra information, and standardizes common ingredient names.
    
    Args:
        ingredient (str): Raw ingredient name
    
    Returns:
        str: Normalized ingredient name
    """
    # Remove quantities, concentrations, and other extra information
    # e.g., "Aqua (Water)*" -> "Aqua", "Glycerin 3%" -> "Glycerin"
    ingredient = re.sub(r'\s*\([^)]*\)', '', ingredient)  # Remove parentheses
    ingredient = re.sub(r'\s*\*.*', '', ingredient)       # Remove asterisk and after
    ingredient = re.sub(r'\s*\d+%', '', ingredient)       # Remove percentages
    ingredient = re.sub(r'\s*\d+\.?\d*\s*(ml|g|oz)', '', ingredient, flags=re.IGNORECASE)  # Remove quantities
    
    # Standardize common ingredient names
    ingredient_lower = ingredient.lower().strip()
    standardization_map = {
        "vitamin c": "Ascorbic Acid",
        "ascorbic acid": "Ascorbic Acid",
        "hyaluronic": "Hyaluronic Acid",
        "hyaluronic acid": "Hyaluronic Acid",
        "niacinamide": "Niacinamide",
        "salicylic": "Salicylic Acid",
        "glycolic": "Glycolic Acid",
        "lactic": "Lactic Acid",
        "retinol": "Retinol",
        "vitamin e": "Tocopherol",
        "tocopherol": "Tocopherol"
    }
    
    # Apply standardization if needed
    for key, value in standardization_map.items():
        if key in ingredient_lower:
            return value
    
    return ingredient.strip()

def group_products_by_ingredients(products_df):
    """
    Group products by similar key ingredients
    
    This function groups products by their key ingredients by:
    1. Splitting ingredients by common separators
    2. Normalizing ingredient names
    3. Creating groups for each key ingredient
    
    Args:
        products_df (pandas.DataFrame): DataFrame containing product data
    
    Returns:
        dict: Dictionary mapping ingredients to lists of products
    """
    # Create a dictionary to store products by ingredient
    ingredient_groups = defaultdict(list)
    
    for _, product in products_df.iterrows():
        ingredients_text = product["Ingredients"]
        if not ingredients_text:
            continue
            
        # Split ingredients by common separators
        ingredients = re.split(r'[,\n|]', ingredients_text)
        
        # Normalize and collect key ingredients
        key_ingredients = set()
        for ingredient in ingredients:
            normalized = normalize_ingredient(ingredient)
            if normalized and len(normalized) > 2:  # Only consider ingredients with more than 2 characters
                key_ingredients.add(normalized.lower())
        
        # Add product to groups for each key ingredient
        for ingredient in key_ingredients:
            ingredient_groups[ingredient].append({
                "Product Name": product["Product Name"],
                "Brand Name": product["Brand Name"],
                "Ingredients": ingredients_text
            })
    
    return ingredient_groups

def main():
    """
    Main function to run the skincare product scraper
    
    This function orchestrates the entire scraping process:
    1. Fetches product data from API or HTML
    2. Extracts and structures product information
    3. Groups products by key ingredients
    4. Creates and saves output files
    """
    # Try to fetch products from API or HTML
    all_products = []
    
    # First try to get data from the API
    data = fetch_products_from_api(0, "skin care")
    
    if data and data.get("data"):
        # If API works, use pagination to get all products
        page = 0
        while True:
            print(f"Fetching page {page}...")
            data = fetch_products_from_api(page, "skin care")
            
            if not data or not data.get("data"):
                break
                
            products = data["data"].get("hits", [])
            all_products.extend(products)
            
            # Check if there are more pages
            if data["data"].get("isFinished", True):
                break
                
            page += 1
            # Add a small delay to be respectful to the server
            time.sleep(1)
    elif data:
        # If we got data from HTML parsing (single page)
        print("Using data from debug.html")
        all_products = data.get("data", {}).get("hits", [])
    else:
        print("❌ Failed to fetch product data.")
        return
    
    print(f"Found {len(all_products)} products")
    
    # Extract product data
    all_data = []
    for product in all_products:
        try:
            data = extract_product_data(product)
            all_data.append(data)
        except Exception as e:
            print(f"Failed to extract data for product: {e}")
    
    if all_data:
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Save to CSV
        df.to_csv("Braxtone_Omusugu_snapklik_products.csv", index=False)
        print("✅ Product data saved to Braxtone_Omusugu_snapklik_products.csv")
        
        # Group products by ingredients
        ingredient_groups = group_products_by_ingredients(df)
        
        # Create grouped output table as specified
        output_data = []
        
        # Calculate product scores (simple approach: length of product name + brand name)
        df_with_scores = df.copy()
        df_with_scores['score'] = df_with_scores['Product Name'].str.len() + df_with_scores['Brand Name'].str.len()
        
        # Convert to dictionary for easier processing
        products_list = df_with_scores.to_dict('records')
        
        # Create a mapping of ingredients to products with scores
        ingredient_to_products = defaultdict(list)
        for product in products_list:
            ingredients_text = product["Ingredients"]
            if ingredients_text:
                ingredients = re.split(r'[,\n|]', ingredients_text)
                for ingredient in ingredients:
                    normalized = normalize_ingredient(ingredient)
                    if normalized and len(normalized) > 2:
                        ingredient_to_products[normalized.lower()].append(product)
        
        # For each ingredient, get top 3 products by score
        for ingredient, products in ingredient_to_products.items():
            # Sort products by score (highest first)
            sorted_products = sorted(products, key=lambda x: x['score'], reverse=True)
            
            # Get top 3 products for this ingredient
            top_products = sorted_products[:3]
            
            for i, product in enumerate(top_products, 1):
                output_data.append({
                    'Key Ingredient': ingredient.title(),
                    'Product Rank': i,
                    'Product Name': product['Product Name'],
                    'Brand': product['Brand Name'],
                    'Price (USD)': f"${product['Price']/100:.2f}" if isinstance(product['Price'], (int, float)) and product['Price'] != "" else str(product['Price']),
                    'Product Score': product['score']
                })
        
        # Create DataFrame and save to CSV
        output_df = pd.DataFrame(output_data)
        output_df.to_csv('Braxtone Omusugu - grouped_skincare_products.csv', index=False)
        print("✅ Results saved to 'Braxtone Omusugu - grouped_skincare_products.csv'")
        
        # Display summary
        print(f"\nSummary: Grouped {len(products_list)} products by key ingredients")
        print(f"Found {len(ingredient_to_products)} unique ingredient groups")
        
        # Show top 5 ingredient groups by product count
        sorted_groups = sorted(ingredient_to_products.items(), key=lambda x: len(x[1]), reverse=True)
        print("\nTop 5 ingredient groups by product count:")
        for ingredient, products in sorted_groups[:5]:
            print(f"  {ingredient.title()}: {len(products)} products")
    else:
        print("❌ No product data scraped.")

if __name__ == "__main__":
    main()
