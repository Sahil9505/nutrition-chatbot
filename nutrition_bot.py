import os
import google.generativeai as genai
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, url_for

# Load environment variables
load_dotenv()

# Configure the Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
SPOONACULAR_API_KEY = os.getenv('SPOONACULAR_API_KEY')

if not GOOGLE_API_KEY:
    print("WARNING: GOOGLE_API_KEY not found in environment variables!")
    print("Make sure you have a .env file with your API key")

if not SPOONACULAR_API_KEY:
    print("WARNING: SPOONACULAR_API_KEY not found in environment variables!")
    print("Make sure you have a .env file with your API key for food facts")

genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

# Nutrition database (simplified local approach instead of Open Food Facts API)
NUTRITION_DATABASE = {
    "apple": {
        "name": "Apple",
        "calories": 52,
        "fat": 0.2,
        "saturated_fat": 0,
        "carbs": 14,
        "sugars": 10,
        "protein": 0.3,
        "fiber": 2.4,
        "description": "A common round fruit with a red, yellow, or green skin and a white flesh."
    },
    "banana": {
        "name": "Banana",
        "calories": 89,
        "fat": 0.3,
        "saturated_fat": 0.1,
        "carbs": 23,
        "sugars": 12,
        "protein": 1.1,
        "fiber": 2.6,
        "description": "A long curved fruit with a yellow skin and soft sweet flesh."
    },
    "orange": {
        "name": "Orange",
        "calories": 43,
        "fat": 0.1,
        "saturated_fat": 0,
        "carbs": 9,
        "sugars": 8,
        "protein": 0.9,
        "fiber": 2.4,
        "description": "A round juicy citrus fruit with a tough bright reddish-yellow rind."
    },
    "sidi ali": {
        "name": "Sidi Ali Mineral Water",
        "brand": "Sidi Ali",
        "calories": 0,
        "fat": 0,
        "saturated_fat": 0,
        "carbs": 0,
        "sugars": 0,
        "protein": 0,
        "sodium": 0.5,
        "calcium": 4.2,
        "magnesium": 1.3,
        "description": "Moroccan natural mineral water brand sourced from springs in the Middle Atlas Mountains. It contains natural minerals and is bottled at the source."
    }
}

# Basic common nutrition terms that don't require API lookup
NUTRITION_KEYWORDS = [
    'nutrition', 'food', 'diet', 'calories', 'protein', 'carbs', 'carbohydrates',
    'fat', 'vitamin', 'mineral', 'nutrient', 'fiber', 'sugar', 'sodium', 'salt',
    'cholesterol', 'meal', 'snack', 'breakfast', 'lunch', 'dinner', 'healthy',
    'unhealthy', 'weight', 'obesity', 'health', 'serving', 'portion', 'ingredient',
    'macro', 'micronutrient', 'supplement', 'nutrition facts', 'label', 'organic',
    'processed', 'natural', 'vegetarian', 'vegan', 'pescatarian', 'keto', 'paleo',
    'mediterranean', 'whole food', 'junk food', 'fast food', 'restaurant', 'recipe',
    'cook', 'bake', 'grill', 'roast', 'boil', 'fry', 'fruit', 'vegetable', 'meat',
    'beverage', 'drink', 'dairy', 'grain'
]

# Cache for food terms to avoid repeated API calls
FOOD_TERMS_CACHE = {}
# Maximum cache size to prevent memory issues
MAX_CACHE_SIZE = 1000

# Common food terms to preload in cache to reduce API calls
COMMON_FOOD_TERMS = [
    'apple', 'banana', 'burger', 'pizza', 'rice', 'chicken', 'beef', 'salad',
    'pasta', 'bread', 'milk', 'cheese', 'yogurt', 'fish', 'egg', 'potato',
    'tomato', 'coffee', 'tea', 'water', 'juice', 'soda', 'cookie'
]

def is_food_term_via_api(term):
    """Check if a term is a food item using the Spoonacular API"""
    global FOOD_TERMS_CACHE
    
    # Check cache first
    if term in FOOD_TERMS_CACHE:
        return FOOD_TERMS_CACHE[term]
        
    # Limit cache size to prevent memory issues
    if len(FOOD_TERMS_CACHE) > MAX_CACHE_SIZE:
        # Clear half of the cache when it gets too big
        keys_to_remove = list(FOOD_TERMS_CACHE.keys())[:len(FOOD_TERMS_CACHE)//2]
        for key in keys_to_remove:
            del FOOD_TERMS_CACHE[key]
    
    if not SPOONACULAR_API_KEY:
        return False
        
    try:
        # Use Spoonacular's autocomplete feature as it's faster and uses less quota
        autocomplete_url = "https://api.spoonacular.com/food/ingredients/autocomplete"
        params = {
            "apiKey": SPOONACULAR_API_KEY,
            "query": term,
            "number": 1
        }
        
        response = requests.get(autocomplete_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # If we get a result, this is likely a food term
        is_food = len(data) > 0
        
        # Cache the result
        FOOD_TERMS_CACHE[term] = is_food
        return is_food
        
    except Exception as e:
        print(f"Error checking if term is food: {e}")
        return False

def is_nutrition_related(question):
    """Check if the question is related to nutrition, food, or diet"""
    question_lower = question.lower()
    
    # First check against our basic nutrition keywords
    if any(keyword in question_lower for keyword in NUTRITION_KEYWORDS):
        return True
    
    # If not found in basic keywords, check individual words against API
    words = question_lower.split()
    # Filter out common short words and stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'is', 'are', 'was', 'were', 'been', 'be', 'as', 'this', 'that', 'these', 'those', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'shall', 'should', 'can', 'could', 'may', 'might', 'must', 'of'}
    
    for word in words:
        # Only check words with 3+ characters to avoid checking common words
        if len(word) >= 3 and word not in stop_words and is_food_term_via_api(word):
            return True
    
    # If longer than one word, try checking 2-word combinations for food items
    if len(words) > 1:
        for i in range(len(words) - 1):
            if words[i] not in stop_words or words[i+1] not in stop_words:
                two_word_term = words[i] + " " + words[i+1]
                if is_food_term_via_api(two_word_term):
                    return True
    
    return False

def is_greeting(message):
    """Check if the message is a greeting"""
    greeting_keywords = [
        'hi', 'hello', 'hey', 'greetings', 'howdy', 'hola', 'namaste', 
        'good morning', 'good afternoon', 'good evening', 'good day',
        'what\'s up', 'sup', 'yo', 'hiya', 'hi there', 'hello there',
        'morning', 'evening', 'afternoon', 'welcome', 'bonjour', 'ciao'
    ]
    
    message_lower = message.lower()
    return any(greeting in message_lower.split() or greeting == message_lower for greeting in greeting_keywords)

def get_welcome_message():
    """Generate a welcome message with suggested questions"""
    welcome = """<strong>Welcome to the Nutrition Facts Guide!</strong><br><br>
    I'm your personal nutrition assistant. I can help you with information about food nutrients, calories, dietary information, and health benefits of different foods.<br><br>
    <strong>Here are some things you can ask me:</strong><br>
    • What are the nutrition facts in an apple?<br>
    • How many calories are in a banana?<br>
    • What nutrients are in salmon?<br>
    • Tell me about the health benefits of spinach<br>
    • Is oatmeal good for breakfast?<br>
    • Compare nutritional value of white rice vs brown rice<br><br>
    What would you like to know about today?"""
    
    return welcome

def extract_food_name(query):
    """Extract potential food name from a query"""
    # Check patterns like "calories in X" or "nutrition of X"
    query_lower = query.lower()
    words = query_lower.split()
    
    # Common prepositions that might appear before food items
    prepositions = ['in', 'of', 'about', 'for', 'from', 'on', 'with', 'without', 'regarding']
    
    # Try to extract food name using prepositions
    for i, word in enumerate(words):
        if word in prepositions and i < len(words) - 1:
            return ' '.join(words[i+1:])
    
    # If no preposition found, check if the query itself might be a food item
    # This enables direct queries like "burger" or "chocolate cake"
    if len(words) <= 3:  # Assuming short queries might be direct food items
        return query_lower
    
    return None

def get_food_info_from_api(food_name):
    """Get food info from Spoonacular API"""
    if not SPOONACULAR_API_KEY:
        return None
        
    try:
        # First try the ingredients search endpoint
        search_url = f"https://api.spoonacular.com/food/ingredients/search"
        params = {
            "apiKey": SPOONACULAR_API_KEY,
            "query": food_name,
            "number": 1,
            "sort": "calories",
            "sortDirection": "desc"
        }
        
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        search_data = response.json()
        
        if search_data.get("results") and len(search_data["results"]) > 0:
            food_id = search_data["results"][0]["id"]
            
            # Get nutrition information for ingredient
            info_url = f"https://api.spoonacular.com/food/ingredients/{food_id}/information"
            info_params = {
                "apiKey": SPOONACULAR_API_KEY,
                "amount": 100,
                "unit": "grams"
            }
            
            info_response = requests.get(info_url, params=info_params)
            info_response.raise_for_status()
            food_data = info_response.json()
            
            # Format the data to match our structure
            food_info = {
                "name": food_data.get("name", "").capitalize(),
                "description": f"Information about {food_data.get('name', '').capitalize()}."
            }
            
            # Extract nutrients
            if "nutrition" in food_data and "nutrients" in food_data["nutrition"]:
                for nutrient in food_data["nutrition"]["nutrients"]:
                    name = nutrient.get("name", "").lower()
                    amount = nutrient.get("amount", 0)
                    
                    if "calories" in name or "energy" in name:
                        food_info["calories"] = amount
                    elif "fat" == name:
                        food_info["fat"] = amount
                    elif "saturated" in name:
                        food_info["saturated_fat"] = amount
                    elif "carbohydrates" in name:
                        food_info["carbs"] = amount
                    elif "sugar" in name:
                        food_info["sugars"] = amount
                    elif "protein" in name:
                        food_info["protein"] = amount
                    elif "fiber" in name:
                        food_info["fiber"] = amount
                    elif "sodium" in name:
                        food_info["sodium"] = amount
                    elif "calcium" in name:
                        food_info["calcium"] = amount
                    elif "magnesium" in name:
                        food_info["magnesium"] = amount
            
            return food_info
        
        # If ingredient search fails, try the food products search as a fallback
        products_url = "https://api.spoonacular.com/food/products/search"
        product_params = {
            "apiKey": SPOONACULAR_API_KEY,
            "query": food_name,
            "number": 1
        }
        
        product_response = requests.get(products_url, params=product_params)
        product_response.raise_for_status()
        product_data = product_response.json()
        
        if product_data.get("products") and len(product_data["products"]) > 0:
            product_id = product_data["products"][0]["id"]
            
            # Get detailed product information
            product_info_url = f"https://api.spoonacular.com/food/products/{product_id}"
            product_info_params = {
                "apiKey": SPOONACULAR_API_KEY
            }
            
            product_info_response = requests.get(product_info_url, params=product_info_params)
            product_info_response.raise_for_status()
            product_info = product_info_response.json()
            
            # Format product data
            food_info = {
                "name": product_info.get("title", "").capitalize(),
                "brand": product_info.get("brand", ""),
                "description": product_info.get("description", f"Information about {product_info.get('title', '').capitalize()}.")
            }
            
            # Extract nutrients if available
            if "nutrition" in product_info and "nutrients" in product_info["nutrition"]:
                for nutrient in product_info["nutrition"]["nutrients"]:
                    name = nutrient.get("name", "").lower()
                    amount = nutrient.get("amount", 0)
                    
                    if "calories" in name or "energy" in name:
                        food_info["calories"] = amount
                    elif "fat" == name:
                        food_info["fat"] = amount
                    elif "saturated" in name:
                        food_info["saturated_fat"] = amount
                    elif "carbohydrates" in name:
                        food_info["carbs"] = amount
                    elif "sugar" in name:
                        food_info["sugars"] = amount
                    elif "protein" in name:
                        food_info["protein"] = amount
                    elif "fiber" in name:
                        food_info["fiber"] = amount
                    elif "sodium" in name:
                        food_info["sodium"] = amount
                    elif "calcium" in name:
                        food_info["calcium"] = amount
                    elif "magnesium" in name:
                        food_info["magnesium"] = amount
            
            return food_info
            
        # If all searches fail, try the recipe search as last resort
        recipe_url = "https://api.spoonacular.com/recipes/complexSearch"
        recipe_params = {
            "apiKey": SPOONACULAR_API_KEY,
            "query": food_name,
            "number": 1,
            "addNutrition": True
        }
        
        recipe_response = requests.get(recipe_url, params=recipe_params)
        recipe_response.raise_for_status()
        recipe_data = recipe_response.json()
        
        if recipe_data.get("results") and len(recipe_data["results"]) > 0:
            recipe = recipe_data["results"][0]
            
            # Format recipe data
            food_info = {
                "name": recipe.get("title", "").capitalize(),
                "description": f"Recipe information for {recipe.get('title', '').capitalize()}."
            }
            
            # Extract nutrients if available
            if "nutrition" in recipe and "nutrients" in recipe["nutrition"]:
                for nutrient in recipe["nutrition"]["nutrients"]:
                    name = nutrient.get("name", "").lower()
                    amount = nutrient.get("amount", 0)
                    
                    if "calories" in name or "energy" in name:
                        food_info["calories"] = amount
                    elif "fat" == name:
                        food_info["fat"] = amount
                    elif "saturated" in name:
                        food_info["saturated_fat"] = amount
                    elif "carbohydrates" in name:
                        food_info["carbs"] = amount
                    elif "sugar" in name:
                        food_info["sugars"] = amount
                    elif "protein" in name:
                        food_info["protein"] = amount
                    elif "fiber" in name:
                        food_info["fiber"] = amount
                    elif "sodium" in name:
                        food_info["sodium"] = amount
                    elif "calcium" in name:
                        food_info["calcium"] = amount
                    elif "magnesium" in name:
                        food_info["magnesium"] = amount
            
            return food_info
        
        return None
    except Exception as e:
        print(f"Error getting food info from API: {e}")
        return None

def get_food_info(food_name):
    """Get food info from our local database or API"""
    food_name_lower = food_name.lower()
    
    # Try exact match in local database
    if food_name_lower in NUTRITION_DATABASE:
        return NUTRITION_DATABASE[food_name_lower]
    
    # Try partial match in local database
    for key in NUTRITION_DATABASE:
        if food_name_lower in key or key in food_name_lower:
            return NUTRITION_DATABASE[key]
    
    # If not found in local database, try the API
    api_result = get_food_info_from_api(food_name)
    if api_result:
        return api_result
    
    return None

def format_nutrition_facts(food_info):
    """Format nutrition facts into a readable HTML format"""
    if not food_info:
        return "No nutrition information found for this food."
    
    name = food_info.get('name', 'Unknown Food')
    brand = food_info.get('brand', '')
    brand_text = f" ({brand})" if brand else ""
    
    # Build nutrition facts string
    nutrition_facts = f"""
    <strong>{name}</strong>{brand_text}<br><br>
    <strong>Nutrition Facts (per 100g/ml):</strong><br>
    """
    
    # Add standard nutrition info
    for key, label in [
        ('calories', 'Calories'),
        ('fat', 'Fat'),
        ('saturated_fat', 'Saturated Fat'),
        ('carbs', 'Carbohydrates'),
        ('sugars', 'Sugars'),
        ('protein', 'Proteins'),
        ('fiber', 'Fiber'),
        ('sodium', 'Sodium'),
        ('calcium', 'Calcium'),
        ('magnesium', 'Magnesium')
    ]:
        if key in food_info and food_info[key] is not None:
            unit = "kcal" if key == 'calories' else "g" if key in ['fat', 'saturated_fat', 'carbs', 'sugars', 'protein', 'fiber'] else "mg"
            nutrition_facts += f"{label}: {food_info[key]} {unit}<br>"
    
    # Add description if available
    if 'description' in food_info and food_info['description']:
        nutrition_facts += f"<br><strong>Description:</strong><br>{food_info['description']}"
    
    return nutrition_facts

def get_response(prompt):
    """Get response from Gemini AI or local database"""
    try:
        if not GOOGLE_API_KEY:
            return "API key not configured. Please set up your GOOGLE_API_KEY in the .env file."
            
        # Check if this is a greeting
        if is_greeting(prompt):
            return get_welcome_message()
            
        if not is_nutrition_related(prompt):
            return "I apologize, but I can only answer questions related to nutrition and food. Please ask about calories, nutrients, dietary information, or other nutritional aspects of different foods."
        
        # Check if this is a direct food item or a food lookup query
        prompt_lower = prompt.lower()
        
        # Define common food query patterns
        food_keywords = ['nutrition', 'calories', 'nutrient', 'nutritional', 'facts', 'info', 'information']
        is_food_query = any(keyword in prompt_lower for keyword in food_keywords)
        
        # Try to extract a food name
        food_name = None
        
        # If it looks like a nutrition query, extract food name
        if is_food_query:
            food_name = extract_food_name(prompt)
        # If it's a short prompt (1-3 words), it might be a direct food name
        elif len(prompt_lower.split()) <= 3:
            food_name = prompt_lower
            
        # If we have a food name, try to get its info
        if food_name:
            food_info = get_food_info(food_name)
            if food_info:
                return format_nutrition_facts(food_info)
        
        # If not a specific food lookup or no match found, use Gemini
        enhanced_prompt = (
            f"As a nutrition expert specializing in food composition and dietary information, please answer this question: {prompt}. "
            "IMPORTANT: Format your response with HTML tags for structure. "
            "Use <br> for line breaks between paragraphs. "
            "Use <strong>text</strong> for bold/headings and <em>text</em> for emphasis. "
            "If you're providing nutrition facts, list them in a structured format with nutrient names and values clearly labeled. "
            "For example: Calories: 100 kcal<br>Protein: 5g<br>Carbohydrates: 15g<br>Fat: 2g "
            "Keep the total response concise and easy to scan."
        )
        
        response = model.generate_content(enhanced_prompt)
        return response.text
    except Exception as e:
        print(f"Error getting response from Gemini: {e}")
        return f"An error occurred: {str(e)}"

def preload_common_food_terms():
    """Preload common food terms into the cache to reduce API calls during use"""
    print("Preloading common food terms into cache...")
    for term in COMMON_FOOD_TERMS:
        FOOD_TERMS_CACHE[term] = True
    print(f"Preloaded {len(COMMON_FOOD_TERMS)} common food terms")

# Create Flask app
app = Flask(__name__, static_folder='static')

# Enable CORS for all routes
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Create directories if they don't exist
os.makedirs('templates', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/api/test', methods=['GET'])
def test():
    """Test endpoint to verify API is working"""
    return jsonify({'status': 'ok', 'message': 'API is working'})

@app.route('/api/food_info', methods=['GET'])
def food_info():
    """Endpoint to get food information from local database"""
    food_name = request.args.get('food_name', '')
    if not food_name:
        return jsonify({'error': 'No food name provided'}), 400
    
    food_data = get_food_info(food_name)
    if not food_data:
        return jsonify({'error': 'Food not found'}), 404
    
    return jsonify({
        'product_name': food_data.get('name'),
        'brand': food_data.get('brand', ''),
        'nutriments': food_data,
        'formatted': format_nutrition_facts(food_data)
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    print("Chat API endpoint called")
    if not request.is_json:
        print("Error: Request is not JSON")
        return jsonify({'error': 'Request must be JSON'}), 400
        
    data = request.get_json()
    if not data:
        print("Error: Invalid JSON data")
        return jsonify({'error': 'Invalid JSON'}), 400
        
    user_message = data.get('message', '')
    if not user_message:
        print("Error: No message provided")
        return jsonify({'error': 'No message provided'}), 400
    
    print(f"Received message: {user_message}")
    
    # Special handling for exit command
    if user_message.lower() == 'byee':
        print("Exit command received, sending goodbye message")
        return jsonify({'response': 'Goodbye! It was nice talking with you. I\'ll close this session now.', 'exit': True})
    
    # Regular message handling
    try:
        response = get_response(user_message)
        print(f"Sending response: {response[:100]}...")
        return jsonify({'response': response})
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'response': f'Sorry, an error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting the Nutrition Facts Guide Web Interface...")
    print("Open your browser and navigate to http://127.0.0.1:5002")
    print(f"API Key configured: {'Yes' if GOOGLE_API_KEY else 'No - Please check your .env file'}")
    
    # Preload food terms 
    if SPOONACULAR_API_KEY:
        preload_common_food_terms()
    else:
        print("Spoonacular API key not found - food term detection will be limited")
    
    app.run(debug=True, port=5002) 