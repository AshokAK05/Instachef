# Instachef: AI-Powered Recipe Chatbot

Instachef is an AI-powered recipe chatbot that helps users discover and cook delicious meals effortlessly. It provides step-by-step cooking instructions, ingredient lists, and links to purchase ingredients via Instamart. The chatbot specializes in Indian cuisine but can also suggest recipes from around the world, supporting multiple Indian languages for an interactive and engaging experience.

## Features
- 🍽️ **Recipe Search**: Ask for recipes, and ChefBot will provide detailed instructions.
- 🛒 **Ingredient List & Translations**: Lists required ingredients with translations in multiple Indian languages.
- 👨‍🍳 **Cooking Instructions**: Step-by-step guidance for meal preparation.
- 😆 **Humor & Engagement**: Chatbot adds a fun and interactive touch to cooking.
- 🛍️ **Instamart Integration**: Links to buy ingredients online.
- 🌐 **Multilingual Support**: Responds in various Indian languages.

## Tech Stack
- **Backend**: Flask (Python)
- **AI Model**: Google Gemini API
- **Frontend**: HTML, CSS (Flask Templates)
- **Environment Variables**: `dotenv`

## Installation
### Prerequisites
Ensure you have Python installed on your system.

### Step 1: Clone the Repository
```sh
git clone https://github.com/yourusername/instachef.git
cd instachef
```

### Step 2: Create a Virtual Environment
```sh
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Step 3: Install Dependencies
```sh
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables
Create a `.env` file in the root directory and add your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

### Step 5: Run the Application
```sh
python main.py
```

The app will be accessible at `http://127.0.0.1:5000/`.

## API Endpoints
### 1. **Chat with ChefBot**
- **Endpoint:** `POST /chat`
- **Description:** Sends a user message and receives a response from ChefBot.
- **Request Body:**
  ```json
  { "message": "How do I make paneer butter masala?" }
  ```
- **Response:**
  ```json
  { "response": "Here's a delicious recipe for Paneer Butter Masala..." }
  ```

### 2. **Get Ingredient Translations**
- **Endpoint:** `GET /get-ingredients/<ingredient>`
- **Description:** Fetches translations for a given ingredient.
- **Example Request:** `GET /get-ingredients/turmeric powder`
- **Response:**
  ```json
  { "ingredient_translations": ["turmeric powder", "हल्दी", "மஞ்சள் தூள்", ...] }
  ```

## Contribution Guidelines
1. Fork the repository.
2. Create a new branch (`feature-branch`).
3. Commit your changes and push to the branch.
4. Create a Pull Request for review.

## License
 MIT License @ 2025 Ashok Kumar S.

## Contact
For any queries or contributions, feel free to reach out:
📧 Email: ashokaak2005@gmail.com


