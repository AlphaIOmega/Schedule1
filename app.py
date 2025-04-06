from flask import Flask, render_template, request, jsonify
import json
import os
import glob
from collections import defaultdict, Counter
from effects import effects_manager, Effect

app = Flask(__name__)

def load_json_file(file_path, default_value=None):
    """Load a JSON file with a fallback to default value if not found."""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            print(f"Warning: JSON file not found at {file_path}")
            return default_value
    except Exception as e:
        print(f"Error loading JSON file {file_path}: {e}")
        return default_value

# Load base costs and agriculture consumables from JSON files
BASE_COSTS_FILE = 'data/base_costs.json'
AGRICULTURE_CONSUMABLES_FILE = 'data/agriculture_consumables.json'

# Load base costs
base_costs_data = load_json_file(BASE_COSTS_FILE, {"base_costs": {}})
base_costs = base_costs_data.get("base_costs", {})

# Load agriculture consumables
agriculture_consumables_data = load_json_file(AGRICULTURE_CONSUMABLES_FILE, {"agriculture_consumables": {}})
agriculture_consumables = agriculture_consumables_data.get("agriculture_consumables", {})

# Function to determine drug type from product ID
def get_drug_type(product_id, product_details):
    """
    Determine the drug type (weed, cocaine, meth) based on the product ID and details.
    
    Args:
        product_id: The ID of the product
        product_details: Dictionary containing product details
        
    Returns:
        str: "weed", "cocaine", "meth", or None if unknown
    """
    if product_id in product_details:
        drug_type = product_details[product_id].get('DrugType')
        if drug_type == 0:
            return "weed"
        elif drug_type == 1:
            return "meth"
        elif drug_type == 2:
            return "cocaine"
    return None

# Fixed version of calculate_agriculture_cost function
def calculate_agriculture_cost(drug_type, soil_type='Soil', additives=None, pseudo_type=None):
    """
    Calculate the total cost of agriculture consumables needed for production.
    Now properly accounts for soil capacity/longevity.
    """
    cost = 0
    
    if drug_type == "weed" or drug_type == "cocaine":
        # Add soil cost (divided by capacity to get cost per grow cycle)
        soil_data = agriculture_consumables[drug_type]["soils"].get(soil_type)
        if soil_data:
            soil_capacity = soil_data.get("capacity", 1)
            soil_cost = soil_data["cost"]
            # Divide soil cost by capacity to get cost per grow cycle
            cost += soil_cost / soil_capacity
        
        # Add seed cost (use the first seed as default)
        if drug_type == "weed":
            seed_cost = agriculture_consumables[drug_type]["seeds"]["OGKush"]["cost"]
        else:  # cocaine
            seed_cost = agriculture_consumables[drug_type]["seeds"]["CocaSeed"]["cost"]
        cost += seed_cost
        
        # Add additives costs if specified (handling multiple additives)
        if additives:
            if isinstance(additives, list):
                # Handle multiple additives
                for additive in additives:
                    if additive in agriculture_consumables[drug_type]["additives"]:
                        cost += agriculture_consumables[drug_type]["additives"][additive]["cost"]
            else:
                # Handle single additive (string) for backward compatibility
                if additives in agriculture_consumables[drug_type]["additives"]:
                    cost += agriculture_consumables[drug_type]["additives"][additives]["cost"]
    
    elif drug_type == "meth":
        # Add costs for acid and phosphorus
        cost += agriculture_consumables["meth"]["chemicals"]["Acid"]["cost"]
        cost += agriculture_consumables["meth"]["chemicals"]["Phosphorus"]["cost"]
        
        # Add pseudo cost
        if pseudo_type and pseudo_type in agriculture_consumables["meth"]["pseudo"]:
            cost += agriculture_consumables["meth"]["pseudo"][pseudo_type]["cost"]
        else:
            # Default to regular Pseudo
            cost += agriculture_consumables["meth"]["pseudo"]["Pseudo"]["cost"]
    
    return cost

# Fixed version of calculate_yield function
def calculate_yield(drug_type, soil_type='Soil', additives=None):
    """
    Calculate the expected yield based on the drug type and inputs.
    No longer incorrectly multiplies by soil capacity.
    """
    if drug_type == "weed":
        # Start with base yield
        base_yield = agriculture_consumables["weed"]["base_yield"]
        
        # Apply PGR effect if in the additives list
        if additives:
            if isinstance(additives, list):
                # Check if PGR is in the list of additives
                if "PGR" in additives:
                    base_yield = agriculture_consumables["weed"]["pgr_yield"]
                
                # Apply additional yield effects from other additives if needed
                # Example: if there are other additives that affect yield
                # for additive in additives:
                #     if additive != "PGR" and agriculture_consumables["weed"]["additives"][additive].get("yield_modifier"):
                #         base_yield *= agriculture_consumables["weed"]["additives"][additive]["yield_modifier"]
            else:
                # Handle single additive (string) for backward compatibility
                if additives == "PGR":
                    base_yield = agriculture_consumables["weed"]["pgr_yield"]
        
        # Return base yield without multiplying by soil capacity
        return base_yield
        
    elif drug_type == "cocaine":
        # Similar logic for cocaine
        base_yield = agriculture_consumables["cocaine"]["base_yield"]
        
        if additives:
            if isinstance(additives, list):
                if "PGR" in additives:
                    base_yield = agriculture_consumables["cocaine"]["pgr_yield"]
                
                # Apply additional yield effects from other additives if needed
            else:
                if additives == "PGR":
                    base_yield = agriculture_consumables["cocaine"]["pgr_yield"]
        
        # Return base yield without multiplying by soil capacity
        return base_yield
        
    elif drug_type == "meth":
        # Meth has a fixed yield
        return agriculture_consumables["meth"]["yield"]
        
    return 0

# Unit cost calculation is the same, but now uses the corrected function results
def calculate_unit_cost(drug_type, soil_type='Soil', additives=None, pseudo_type=None):
    """
    Calculate the production cost per unit.
    Now uses corrected agriculture cost and yield calculations.
    """
    ag_cost = calculate_agriculture_cost(drug_type, soil_type, additives, pseudo_type)
    product_yield = calculate_yield(drug_type, soil_type, additives)
    
    if product_yield > 0:
        return ag_cost / product_yield
    return 0

def calculate_ingredient_costs_from_crafting_tree(product_id, products_data):
    """
    Calculate the total cost of base ingredients required to craft a product
    by analyzing its complete crafting tree.
    
    Args:
        product_id: The ID of the product to calculate costs for
        products_data: Dictionary of product data including recipes
        
    Returns:
        int: The total cost of all base ingredients
    """
    from collections import Counter
    
    # Create empty dictionaries for building the crafting tree
    product_details = {}
    name_map = {}
    
    # Build the crafting tree for this product
    crafting_tree = build_crafting_tree(product_id, products_data, product_details, name_map)
    
    # Counter to track ingredient counts
    ingredient_counts = Counter()
    
    # Process each step in the crafting tree
    for step in crafting_tree:
        # Only count base ingredients (not intermediate products)
        for ingredient in step.get('ingredients', []):
            item_id = ingredient['id'].lower()
            if item_id in base_costs:
                ingredient_counts[item_id] += 1
    
    # Calculate the total cost
    total = sum(base_costs.get(item, 0) * count for item, count in ingredient_counts.items())
    
    # Add gasoline cost for cocaine production
    drug_type = get_drug_type(product_id, product_details)
    if drug_type == "cocaine":
        # Add the cost of one can of gasoline ($5)
        total += 5
    
    # Optional debug output
    print(f"\n🧪 Final ingredient breakdown for {product_id}:")
    for item, count in ingredient_counts.items():
        print(f"  - {item}: x{count} (${base_costs.get(item, 0)} each)")
    if drug_type == "cocaine":
        print(f"  - gasoline: x1 ($5 each) [automatically added for cocaine]")
    print(f"➡️ Total: ${total}")
    
    return total


def calculate_total_ingredient_costs(products_data):
    from collections import Counter

    recipe_map = {r['Output']: (r['Product'], r['Mixer']) for r in products_data.get('MixRecipes', [])}
    discovered = products_data.get('DiscoveredProducts', [])

    def walk_chain(pid):
        chain = []
        seen = set()

        while pid in recipe_map:
            if pid in seen:
                print(f"⛔ Infinite loop prevented: {pid} already seen")
                break
            seen.add(pid)

            product, mixer = recipe_map[pid]
            chain.append((product, mixer))

            if product == pid:
                print(f"⚠️ Self-reference (ignored): {pid} → {product}")
                break

            pid = product  # follow only the product side down

        return chain

    ingredient_costs = {}

    for pid in discovered:
        chain = walk_chain(pid)
        ingredient_counts = Counter()

        for product, mixer in chain:
            for part in [product, mixer]:
                key = part.lower()
                if key in base_costs:
                    ingredient_counts[key] += 1

        if pid.lower() == "afghancake":
            print(f"\n🧪 Final breakdown for AfghanCake:")
            for item, count in ingredient_counts.items():
                print(f"  - {item}: x{count} (${base_costs[item]} each)")
            print(f"➡️ Total: ${sum(base_costs[k] * v for k, v in ingredient_counts.items())}")

        total_cost = sum(base_costs[k] * v for k, v in ingredient_counts.items())
        ingredient_costs[pid.lower()] = total_cost

    return ingredient_costs

# Calculate the number of mixes required to create each product - FIXED VERSION
def calculate_mix_counts(products_data):
    """
    Calculate the number of mixes required to create each product.
    Properly accounts for all paths in the recipe tree.
    """
    recipes = products_data.get('MixRecipes', [])
    
    # Create recipe map
    recipe_map = {}
    for recipe in recipes:
        output = recipe['Output']
        product = recipe['Product']
        mixer = recipe['Mixer']
        if output not in recipe_map:
            recipe_map[output] = []
        recipe_map[output].append((product, mixer))

    # Find base products (those that aren't outputs of any recipe)
    all_outputs = set(recipe_map.keys())
    all_ingredients = set()
    for recipes_list in recipe_map.values():
        for product, mixer in recipes_list:
            all_ingredients.add(product)
            all_ingredients.add(mixer)
    
    base_products = all_ingredients - all_outputs
    
    # Initialize mix counts
    mix_counts = {}
    
    def get_total_mix_count(product_id, visited=None):
        # Avoid infinite recursion
        if visited is None:
            visited = set()
        if product_id in visited:
            return 0
        visited.add(product_id)
        
        # If we've already calculated this, return it
        if product_id in mix_counts:
            return mix_counts[product_id]
        
        # Base case: if it's a base product or has no recipe
        if product_id in base_products or product_id not in recipe_map:
            mix_counts[product_id] = 0
            return 0
        
        # Get all possible recipes for this product
        recipes_list = recipe_map[product_id]
        
        # Calculate total mixes for each recipe
        total_mixes = 0
        for product, mixer in recipes_list:
            # Current mix (1) + mixes required for ingredients
            product_mixes = get_total_mix_count(product, visited.copy()) 
            mixer_mixes = get_total_mix_count(mixer, visited.copy())
            
            recipe_mixes = 1 + product_mixes + mixer_mixes
            # Use the maximum count if we have multiple recipes
            total_mixes = max(total_mixes, recipe_mixes)
        
        mix_counts[product_id] = total_mixes
        return total_mixes
    
    # Calculate mix counts for all products
    for product_id in products_data.get('DiscoveredProducts', []):
        if product_id not in mix_counts:
            get_total_mix_count(product_id)
    
    return mix_counts

# Extract all unique effects from products
def extract_all_effects(product_details):
    """
    Extract all unique effects from all products.
    
    Args:
        product_details: Dictionary of product details
    
    Returns:
        List of unique effect names
    """
    all_effects = set()
    
    for product in product_details.values():
        if 'Properties' in product:
            all_effects.update(product['Properties'])
    
    return sorted(list(all_effects))

# Ensure data directories exist and create if they don't
def ensure_data_directories():
    """Ensure all required data directories exist."""
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('data/CreatedProducts', exist_ok=True)
    
    # Create base JSON files if they don't exist
    if not os.path.exists(BASE_COSTS_FILE):
        with open(BASE_COSTS_FILE, 'w') as f:
            json.dump({"base_costs": base_costs}, f, indent=2)
        print(f"Created base costs JSON file at {BASE_COSTS_FILE}")
    
    if not os.path.exists(AGRICULTURE_CONSUMABLES_FILE):
        with open(AGRICULTURE_CONSUMABLES_FILE, 'w') as f:
            json.dump({"agriculture_consumables": agriculture_consumables}, f, indent=2)
        print(f"Created agriculture consumables JSON file at {AGRICULTURE_CONSUMABLES_FILE}")
    
    # Create effects.json if it doesn't exist
    effects_json_path = 'data/effects.json'
    if not os.path.exists(effects_json_path):
        # Extract default effects from the effects manager
        all_effects = effects_manager.get_all_effects()
        effects_data = {
            "effects": [
                {
                    "name": effect.name,
                    "multiplier": effect.multiplier,
                    "type": effect.type,
                    "description": effect.description,
                    "color": effect.color
                }
                for effect in all_effects
            ]
        }
        
        with open(effects_json_path, 'w') as f:
            json.dump(effects_data, f, indent=2)
        print(f"Created effects JSON file at {effects_json_path}")

# Load product data from the provided JSON files in the correct locations
def load_product_data():
    # Ensure data directories exist
    ensure_data_directories()
    
    # Load Products.json from data directory
    try:
        with open('data/Products.json', 'r') as f:
            products_data = json.load(f)
        print(f"Successfully loaded Products.json from data directory")
    except Exception as e:
        print(f"Error loading Products.json: {e}")
        products_data = {
            'DiscoveredProducts': [],
            'MixRecipes': [],
            'ProductPrices': []
        }
    
    # Load individual product files from CreatedProducts directory
    product_details = {}
    
    # First, try to load files based on DiscoveredProducts list in Products.json
    if 'DiscoveredProducts' in products_data:
        for product_id in products_data['DiscoveredProducts']:
            product_file = f'data/CreatedProducts/{product_id}.json'
            try:
                if os.path.exists(product_file):
                    with open(product_file, 'r') as f:
                        product_details[product_id] = json.load(f)
                    print(f"Successfully loaded {product_file}")
            except Exception as e:
                print(f"Error loading {product_file}: {e}")
    
    # If no products were loaded through the list, scan the directory directly
    if not product_details:
        print("No products loaded from DiscoveredProducts list, scanning directory...")
        product_files = glob.glob('data/CreatedProducts/*.json')
        
        for product_file in product_files:
            try:
                with open(product_file, 'r') as f:
                    product_data = json.load(f)
                    
                # Get product ID from the filename or the ID field in the JSON
                if 'ID' in product_data:
                    product_id = product_data['ID']
                else:
                    product_id = os.path.basename(product_file).replace('.json', '')
                
                product_details[product_id] = product_data
                
                # Add to discovered products if not already there
                if product_id not in products_data['DiscoveredProducts']:
                    products_data['DiscoveredProducts'].append(product_id)
                    
                print(f"Loaded {product_file} as {product_id}")
            except Exception as e:
                print(f"Error loading {product_file}: {e}")
    
    # Calculate mix counts for all products
    mix_counts = calculate_mix_counts(products_data)
    
    print(f"Total products loaded: {len(product_details)}")
    return products_data, product_details, mix_counts

# Create a mapping of product IDs to names
def create_product_name_map(product_details):
    name_map = {}
    for product_id, details in product_details.items():
        if 'Name' in details:
            name_map[product_id] = details['Name']
        else:
            name_map[product_id] = product_id  # Fallback to ID if name not available
    return name_map

# Build a crafting tree for a product
def build_crafting_tree(product_id, products_data, product_details, name_map, mix_counts=None):
    """
    Build a crafting tree for a product without duplicating nodes.
    Each product appears only once in the tree, with its complete recipe.
    
    Args:
        product_id: ID of the product to build a tree for
        products_data: Dictionary containing MixRecipes and other data
        product_details: Dictionary of product details
        name_map: Mapping of product IDs to names
        mix_counts: Dictionary of product mix counts (optional)
        
    Returns:
        List of crafting steps with ingredients
    """
    # Create a dictionary to map products to their ingredients
    recipe_map = {}
    for recipe in products_data['MixRecipes']:
        output = recipe['Output']
        product = recipe['Product']
        mixer = recipe['Mixer']
        if output not in recipe_map:
            recipe_map[output] = []
        recipe_map[output].append({
            'product': product,
            'mixer': mixer
        })
    
    # Track processed products to avoid duplication
    processed_products = set()
    
    # Build the crafting path
    crafting_path = []
    
    def add_to_crafting_path(current_id):
        """Recursively add products to the crafting path, depth-first"""
        # Skip if already processed
        if current_id in processed_products:
            return
        
        # Mark as processed
        processed_products.add(current_id)
        
        # Skip if no recipe exists
        if current_id not in recipe_map:
            return
        
        # Process ingredients (depth-first)
        recipes = recipe_map[current_id]
        # Use the first recipe (we could choose based on efficiency if desired)
        recipe = recipes[0]
        
        ingredient1_id = recipe['product']
        ingredient2_id = recipe['mixer']
        
        # Process ingredients first (depth-first)
        add_to_crafting_path(ingredient1_id)
        add_to_crafting_path(ingredient2_id)
        
        # Get ingredient names
        ingredient1_name = name_map.get(ingredient1_id, ingredient1_id)
        ingredient2_name = name_map.get(ingredient2_id, ingredient2_id)
        
        # Determine which ingredient is a "real product" and which is a "mixer item"
        # Check if ingredients are actual products in our database
        ingredient1_is_product = ingredient1_id in product_details
        ingredient2_is_product = ingredient2_id in product_details
        
        # Decide on the order
        if ingredient1_is_product and not ingredient2_is_product:
            # First ingredient is a product, second is an item - keep original order
            pass
        elif not ingredient1_is_product and ingredient2_is_product:
            # First ingredient is an item, second is a product - swap them
            ingredient1_id, ingredient2_id = ingredient2_id, ingredient1_id
            ingredient1_name, ingredient2_name = ingredient2_name, ingredient1_name
        
        # Add current product to the crafting path
        product_name = name_map.get(current_id, current_id)
        
        # Add mix count info if available
        mix_count_info = ""
        if mix_counts and current_id in mix_counts:
            count = mix_counts[current_id]
            mix_count_info = f" ({count} {'mix' if count == 1 else 'mixes'})"
        
        crafting_path.append({
            'id': current_id,
            'name': product_name,
            'mix_count': mix_counts.get(current_id, 0) if mix_counts else 0,
            'ingredients': [
                {'id': ingredient1_id, 'name': ingredient1_name},
                {'id': ingredient2_id, 'name': ingredient2_name}
            ]
        })
    
    # Start building the tree from the target product
    add_to_crafting_path(product_id)
    
    # Add the final product if it's not in the path yet (e.g., if it's a base product)
    if product_id not in processed_products:
        product_name = name_map.get(product_id, product_id)
        crafting_path.append({
            'id': product_id,
            'name': product_name,
            'mix_count': mix_counts.get(product_id, 0) if mix_counts else 0,
            'ingredients': []
        })
    
    # Reverse the path so the target product is first
    crafting_path.reverse()
    
    return crafting_path

# Function to calculate combined cost with multiple additives
def calculate_combined_cost(drug_type, soil_type, additives, pseudo_type, yield_amount, mixing_cost):
    """
    Calculate the combined cost with multiple additives.
    """
    # Calculate agriculture cost
    agriculture_cost = calculate_agriculture_cost(drug_type, soil_type, additives, pseudo_type)

    apc = agriculture_cost / yield_amount if yield_amount > 0 else 0
    ctc = (agriculture_cost + mixing_cost) / yield_amount if yield_amount > 0 else 0
    return apc, ctc

@app.route('/')
def index():
    products_data, product_details, mix_counts = load_product_data()
    name_map = create_product_name_map(product_details)

    # Create a dictionary to map product IDs to prices
    price_map = {item['String']: item['Int'] for item in products_data.get('ProductPrices', [])}

    # Calculate ingredient costs for all products using the improved method
    ingredient_costs = {}
    for product_id in products_data.get('DiscoveredProducts', []):
        try:
            cost = calculate_ingredient_costs_from_crafting_tree(product_id, products_data)
            ingredient_costs[product_id.lower()] = cost
        except Exception as e:
            print(f"Error calculating cost for {product_id}: {e}")
            ingredient_costs[product_id.lower()] = 0

    # Extract all unique effects for filtering
    all_effects = extract_all_effects(product_details)

    # Calculate effect distribution for statistics
    effect_counts = Counter()
    for product in product_details.values():
        if 'Properties' in product:
            effect_counts.update(product['Properties'])

    # Get effect details for all effects
    effects_data = {}
    for effect_name in all_effects:
        try:
            effect = effects_manager.get_effect(effect_name)
            if effect:
                effects_data[effect_name] = {
                    'type': effect.type,
                    'description': effect.description,
                    'multiplier': effect.multiplier,
                    'count': effect_counts[effect_name]
                }
        except Exception as e:
            print(f"Error processing effect '{effect_name}': {e}")

    # Get the max mix count for the mix count filter
    max_mix_count = max(mix_counts.values()) if mix_counts else 0

    return render_template('index.html', 
                           products=products_data['DiscoveredProducts'],
                           ingredient_costs=ingredient_costs,
                           product_details=product_details,
                           name_map=name_map,
                           price_map=price_map,
                           mix_counts=mix_counts,
                           all_effects=all_effects,
                           effects_data=effects_data,
                           max_mix_count=max_mix_count)

@app.route('/product/<product_id>')
def product_detail(product_id):
    products_data, product_details, mix_counts = load_product_data()
    name_map = create_product_name_map(product_details)
    
    # Get product details
    product = product_details.get(product_id)
    
    # If product not found, return 404
    if not product:
        return f"Product {product_id} not found", 404
    
    # Create a dictionary to map product IDs to prices
    price_map = {item['String']: item['Int'] for item in products_data.get('ProductPrices', [])}
    
    # Get the price for this product
    price = price_map.get(product_id, 0)
    
    # Get the mix count for this product
    mix_count = mix_counts.get(product_id, 0)
    
    # Build the crafting tree
    crafting_tree = build_crafting_tree(product_id, products_data, product_details, name_map)
    
    # Calculate ingredient costs directly from the crafting tree
    ingredient_cost = calculate_ingredient_costs_from_crafting_tree(product_id, products_data)
    
    # Determine the drug type for this product
    drug_type = get_drug_type(product_id, product_details)
    
    # Agriculture options based on drug type
    agriculture_options = {}
    if drug_type:
        if drug_type == "weed" or drug_type == "cocaine":
            agriculture_options["soils"] = agriculture_consumables[drug_type]["soils"]
            agriculture_options["additives"] = agriculture_consumables[drug_type]["additives"]
            if drug_type == "weed":
                agriculture_options["seeds"] = agriculture_consumables[drug_type]["seeds"]
        elif drug_type == "meth":
            agriculture_options["pseudo"] = agriculture_consumables[drug_type]["pseudo"]
    
    # Get effect details for each property
    effects_data = {}
    if product.get('Properties'):
        for prop in product['Properties']:
            effect = effects_manager.get_effect(prop)
            if effect:
                effects_data[prop] = {
                    'type': effect.type,
                    'description': effect.description,
                    'multiplier': effect.multiplier,
                    'color': effect.color or None  # Use color from JSON if available
                }
    
    return render_template('product_detail.html', 
                          product_id=product_id,
                          ingredient_cost=ingredient_cost,
                          product=product,
                          price=price,
                          mix_count=mix_count,
                          crafting_tree=crafting_tree,
                          product_details=product_details,
                          name_map=name_map,
                          price_map=price_map,
                          mix_counts=mix_counts,
                          effects_data=effects_data,
                          drug_type=drug_type,
                          agriculture_options=agriculture_options,
                          agriculture_consumables=agriculture_consumables)

@app.route('/api/calculate-agriculture-cost', methods=['POST'])
def api_calculate_agriculture_cost():
    data = request.json
    drug_type = data.get('drug_type')
    soil_type = data.get('soil_type')
    
    # Handle both single "additive" and multiple "additives" parameters
    additives = data.get('additives', [])
    if not additives and 'additive' in data:
        # For backward compatibility
        additive = data.get('additive')
        if additive:
            additives = [additive] if not isinstance(additive, list) else additive
    
    pseudo_type = data.get('pseudo_type')

    ag_cost = calculate_agriculture_cost(drug_type, soil_type, additives, pseudo_type)
    product_yield = calculate_yield(drug_type, soil_type, additives)
    unit_cost = calculate_unit_cost(drug_type, soil_type, additives, pseudo_type)
    mixing_cost = data.get('mixing_cost', 0)
    
    # Calculate combined cost with mixing cost
    total_cost = ag_cost
    combined_cost = total_cost / product_yield + mixing_cost / product_yield if product_yield > 0 else 0
    selling_price = data.get('selling_price', 0)
    net_profit = selling_price - combined_cost
    
    return jsonify({
        'total_cost': ag_cost,
        'yield': product_yield,
        'unit_cost': unit_cost,
        'combined_cost': combined_cost,
        'net_profit': net_profit
    })

@app.route('/api/products')
def get_products():
    products_data, product_details, _ = load_product_data()
    return jsonify(products_data['DiscoveredProducts'])

@app.route('/api/product/<product_id>')
def get_product(product_id):
    _, product_details, _ = load_product_data()
    
    if product_id in product_details:
        return jsonify(product_details[product_id])
    else:
        return jsonify({'error': f'Product {product_id} not found'}), 404
    
    # Start the Flask app
app.run(debug=True)
