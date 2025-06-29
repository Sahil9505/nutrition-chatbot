# Nutrition Facts Chatbot

An interactive chatbot that provides detailed nutritional information about foods and meals. The chatbot is powered by Google's Gemini AI and Spoonacular API for comprehensive food data, featuring a modern, responsive web interface with a dynamic gradient background powered by Framer Motion.

## Features

- **Nutrition-Focused AI**: Specialized in answering questions about nutrients, calories, and dietary information
- **Comprehensive Food Database**: Uses Spoonacular API to access nutrition data for thousands of food items
- **Dynamic Food Term Detection**: Automatically recognizes food terms in user queries using API-based verification
- **Modern Web Interface**: Featuring a beautiful animated gradient background using Framer Motion
- **Responsive Design**: Works well on desktop and mobile devices
- **Nutrition Facts Tables**: Auto-formats nutrition information into readable tables

## API Integration

The chatbot integrates with two key APIs:

1. **Google Gemini API**: Provides the conversational AI capabilities, allowing the chatbot to understand and respond to user queries naturally.

2. **Spoonacular API**: Used for two main purposes:
   - **Food Data Retrieval**: Fetches detailed nutrition information for thousands of food items
   - **Food Term Detection**: Dynamically recognizes food terms in user queries instead of relying on a hardcoded list
   - **Efficient Caching**: Implemented to reduce API calls and improve response times

## Web Interface

The web interface has been designed with a modern, clean aesthetic that emphasizes healthy eating:

- Animated gradient background with soothing green tones using Framer Motion
- Clean, light-themed chat interface with nutrition-focused design elements
- Automatic formatting of nutrition data into structured tables
- Typing indicators for a more interactive experience
- Smooth animations and transitions

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Google API key for Gemini AI
- Spoonacular API key for food nutrition data

### Installation

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your API keys:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   SPOONACULAR_API_KEY=your_spoonacular_api_key_here
   ```

### Running the Web Interface

Run the Flask web application:

```
python web_chatbot_ui.py
```

Then open your browser and navigate to `http://127.0.0.1:5002` to use the chatbot.

### Running the Command Line Interface

For a simpler experience, you can also use the command-line version:

```
python chatbot.py
```

## Usage

1. Ask questions about nutrition facts, calories, or nutrients in foods
2. The AI will respond with relevant nutritional information
3. Type "byee" to exit the conversation

## Examples of Questions

- "What nutrients are in an apple?"
- "How many calories are in a serving of salmon?"
- "What's the nutritional difference between white and brown rice?"
- "Is spinach a good source of iron?"
- "How much protein is in chicken breast?"
- "What's the recommended daily intake of vitamin C?"
- Simply typing "burger" or any food name will return nutrition facts

## API Usage Optimization

The system is designed to minimize API usage while maximizing functionality:

- **Caching System**: Food terms are cached to avoid repeated API calls
- **Preloading Common Terms**: Popular food terms are preloaded during startup
- **Smart Text Processing**: Query text is processed to avoid unnecessary API calls
- **Hierarchical Search**: Local database is checked before making API calls

## License

This project is open source and available under the MIT License.

## Credits

- Built with Flask and Framer Motion
- Powered by Google's Gemini 1.5 Flash API and Spoonacular API 