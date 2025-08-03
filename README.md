
# Snapklik Skincare Product Scraper

A Python script that scrapes skincare product data from [Snapklik.com](https://snapklik.com), extracts key product details, categorizes them by inferred ingredients, and outputs clean, grouped CSV files for analysis.

---

## Features

- Scrapes skincare product listings via Snapklik’s **API** or an **HTML fallback**
- Extracts product data including **name, brand, price, categories, ingredients, concerns, and size**
- Heuristically infers **key ingredients** from category metadata
- Groups and ranks products by similar **key ingredients**
- Outputs two CSV files:
- `snapklik_products.csv`: Raw product data
- `grouped_skincare_products.csv`: Ingredient-grouped product rankings

---

## Output Files

| File Name                       | Description                                         |
|---------------------------------|-----------------------------------------------------|
| `snapklik_products.csv`         | Raw product data including all extracted fields     |
| `grouped_skincare_products.csv` | Grouped and ranked products by inferred key ingredients |

---

## How It Works

1. **Data Collection**
   - Queries Snapklik’s search API using pagination
   - Falls back to parsing `debug.html` if the API fails

2. **Data Extraction**
   - Parses fields like name, brand, price, description, image, category
   - Extracts heuristic **ingredient keywords** from categories

3. **Ingredient Grouping**
   - Normalizes ingredient names (e.g., “vitamin C” → “Ascorbic Acid”)
   - Groups and ranks top products per ingredient

4. **Export**
   - Saves a raw product dataset and a ranked ingredient-grouped CSV

---

## 📋 Requirements

- Python 3.7+
- Required Python packages:
  ```bash
  pip install pandas requests


## Usage

1. Clone the repository or download the script.
2. (Optional) Place a fallback HTML file named `debug.html` in the same directory.
3. Run the script:

```bash
python skincare_scraper.py
```

---

## Example Output

**Grouped Products (CSV Sample):**

| Key Ingredient | Product Rank | Product Name             | Brand      | Price (USD) | Product Score |
|----------------|--------------|--------------------------|------------|-------------|----------------|
| Niacinamide    | 1            | Brightening Face Serum   | Glow Co.   | $19.99      | 52             |
| Niacinamide    | 2            | Pore Minimizing Cream    | SkinLabs   | $23.49      | 47             |
| Niacinamide    | 3            | Night Repair Toner       | Beauty Fix | $17.89      | 44             |

---

## Notes

- **Rate-limiting:** A 1-second delay is added between API page calls.
- **Fallback HTML parsing** is supported for offline debugging or if API access is blocked.
- **Ingredients are heuristic-based**, since Snapklik doesn’t expose actual ingredient lists.

---

## Potential Improvements

- Use real ingredient fields if Snapklik exposes them in the future
- Add support for skincare concern classification using ML/NLP
- Expand heuristic keyword detection with a larger taxonomy

---

## Author

**Braxtone Omusugu**  
Open to contributions, improvements, and feedback!

---

## License

This project is open-source and available under the **MIT License**.