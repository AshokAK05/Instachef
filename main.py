from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory
import google.generativeai as genai
from dotenv import load_dotenv
import os
load_dotenv()



app = Flask(__name__)
  # Replace with a strong secret key in production

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
# Configure the Gemini API
  # Replace with your actual Gemini API key

# Define the generation parameters
generation_config = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 50,
    "max_output_tokens": 4096,
    "response_mime_type": "text/plain",
}

# Create the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction=(
        "Chatbot Name: ChefBot\n\nPersona: ChefBot is your friendly virtual chef, always ready to share delicious recipes with a touch of humor and charm. It specializes in Indian cuisine but can also provide recipes from around the world.\n\nMain Functionality:\n\nRecipe Search: Users can ask ChefBot for recipes of various dishes, with a focus on Indian cuisine.\nIngredient List: ChefBot provides a highlighted list of ingredients required for each recipe, along with links to purchase them from Instamart.\nCooking Instructions: ChefBot gives step-by-step cooking instructions in a fun and easy-to-follow manner.\nLanguages:Chefbot can response in any languages in India the user speak In.\nHumor: ChefBot sprinkles jokes and light-hearted comments to make cooking a delightful experience.\nSample Interaction:\n\nUser: Hi ChefBot! I'm in the mood for some paneer butter masala tonight. Can you help me with a recipe?\n\nChefBot: Oh, you've got excellent taste! Paneer butter masala is a star of Indian cuisine. Get your apron ready! Here's what you'll need:\n\nPaneer\nButter (of course!)\nTomatoes\nCream\nSpices: garam masala, turmeric, cumin\nFresh coriander for garnish\nFeeling hungry already?\nUser: Yum! What's the key to a rich, creamy gravy?\n\nChefBot: Ah, the magic is in slow cooking and generous butter. But remember, don't taste too much while cooking or there won’t be any left for dinner! 😄 Ready for the instructions?\n\nUser: Yes, please! How do I make it?\n\nChefBot: Step 1: Sauté onions and spices in butter. Step 2: Add tomatoes and simmer until soft. Step 3: Blend to a smooth sauce. Step 4: Add paneer cubes and cream, and let the magic happen. Garnish with coriander and serve with naan or rice. You’ve just made restaurant-worthy paneer butter masala!\n\nUser: That sounds delicious! Thanks, ChefBot!\n\nChefBot: My pleasure! Enjoy, and remember, I’m always here to spice up your kitchen with more recipes. Happy cooking!\n\n"    ),
)

# Initialize chat session
chat_session = model.start_chat(history=[])

# Define common ingredients used in most dishes
common_ingredients = {
    "turmeric powder": ["turmeric powder", "हल्दी", "மஞ்சள் தூள்", "ಹರಿದಿ ಪುಡಿ", "పసుపు పొడి", "হলুদ গুঁড়ো"],
    "red chili powder": ["red chili powder", "लाल मिर्च पाउडर", "சிவப்பு மிளகாய் தூள்", "ಕೆಂಪು ಮೆಣಸಿನ ಪುಡಿ", "ఎర్ర మిర్చి పొడి", "লাল মরিচ গুঁড়ো"],
    "coriander powder": ["coriander powder", "धनिया पाउडर", "கொத்தமல்லி தூள்", "ಕೊತ್ತಂಬರಿ ಪುಡಿ", "ధనియాల పొడి", "ধনে গুঁড়ো"],
    "cumin powder": ["cumin powder", "जीरा पाउडर", "சீரக தூள்", "ಜೀರಿಗೆ ಪುಡಿ", "జీలకర్ర పొడి", "জিরা গুঁড়ো"],
    "mustard seeds": ["mustard seeds", "सरसों के बीज", "கடுகு விதைகள்", "ಸಾಸಿವೆ", "ఆవాలు", "সরষের বীজ"],
    "fennel seeds": ["fennel seeds", "सौंफ", "பெருஞ்சீரகம்", "ಸೊಂಪು", "సోంపు", "মৌরি"],
    "fenugreek seeds": ["fenugreek seeds", "मेथी के बीज", "வெந்தயம்", "ಮೆಂತ್ಯ", "మెంతులు", "মেথি বীজ"],
    "clove": ["clove", "लौंग", "கிராம்பு", "ಲವಂಗ", "లవంగాలు", "লবঙ্গ"],
    "cardamom": ["cardamom", "इलायची", "ஏலக்காய்", "ಎಲಕ್ಕಿ", "ఏలకులు", "এলাচ"],
    "cinnamon": ["cinnamon", "दालचीनी", "இலவங்கப்பட்டை", "ಚಕ್ಕೆ", "దాల్చిన చెక్క", "দারচিনি"],
    "black pepper": ["black pepper", "काली मिर्च", "கருப்பு மிளகு", "ಕಪ್ಪು ಮೆಣಸು", "నల్ల మిరియాలు", "গোলমরিচ"],
    "bay leaf": ["bay leaf", "तेज पत्ता", "பிரியாணி இலை", "ಬಿರಿಯಾನಿ ಎಲೆ", "బిర్యానీ ఆకు", "তেজপাতা"],
    "star anise": ["star anise", "चक्र फूल", "அனிசிப் பூ", "ಚಕ್ರಫುಲ್", "అనసపువ్వు", "তারা ফুল"],
    "asafoetida": ["asafoetida", "हींग", "பெருங்காயம்", "ಇಂಗು", "ఇంగువ", "হিং"],
    "garam masala": ["garam masala", "गरम मसाला", "கரம் மசாலா", "ಗರಂ ಮಸಾಲಾ", "గరమ్ మసాలా", "গরম মসলা"],
    "amchur powder": ["amchur powder", "अमचूर पाउडर", "மாங்காய் தூள்", "ಅಮಚೂರ್ ಪುಡಿ", "అమ్చూర్ పొడి", "আমচুর গুঁড়ো"],
    "kasuri methi": ["kasuri methi", "कसूरी मेथी", "கசூரி வெந்தயம்", "ಕಸೂರಿ ಮೆಂತ್ಯ", "కసూరి మెంతి", "কাসুরি মেথি"],
    "chat masala": ["chat masala", "चाट मसाला", "சாட் மசாலா", "ಚಾಟ್ ಮಸಾಲಾ", "చాట్ మసాలా", "চাট মসলা"],
    "urad dal": ["urad dal", "उड़द दाल", "உளுந்து", "ಉದ್ದಿನ ಬೇಳೆ", "మినప్పప్పు", "বুট ডাল"],
    "toor dal": ["toor dal", "तूर दाल", "துவரம் பருப்பு", "ತೊಗರಿ ಬೇಳೆ", "కందిపప్పు", "তুর ডাল"],
    "chana dal": ["chana dal", "चना दाल", "கடலை பருப்பு", "ಕಡಲೆ ಬೇಳೆ", "శనగపప్పు", "ছোলা ডাল"],
    "masoor dal": ["masoor dal", "मसूर दाल", "மசூர் பருப்பு", "ಮಸೂರು ಬೇಳೆ", "మసూరి పప్పు", "মসুর ডাল"],
    "moong dal": ["moong dal", "मूंग दाल", "பயறு பருப்பு", "ಹೆಸರು ಬೇಳೆ", "పెసరపప్పు", "মুগ ডাল"],
    "rajma": ["rajma", "राजमा", "ராஜ்மா", "ರಾಜ್ಮಾ", "రాజ్మా", "রাজমা"],
    "kabuli chana": ["kabuli chana", "काबुली चना", "காபூலி சுண்டல்", "ಕಾಬುಲಿ ಕಡಲೆ", "కాబూలీ శనగలు", "কাবুলি ছোলা"],
    "basmati rice": ["basmati rice", "बासमती चावल", "பாசுமதி அரிசி", "ಬಾಸ್ಮತಿ ಅಕ್ಕಿ", "బాస్మతి బియ్యం", "বাসমতি চাল"],
    "sona masoori rice": ["sona masoori rice", "सोना मसूरी चावल", "சோனா மசூரி அரிசி", "ಸೋಣಾ ಮಸೂರಿ ಅಕ್ಕಿ", "సోనా మసూరి బియ్యం", "সোনা মসূরি চাল"],
    "brown rice": ["brown rice", "ब्राउन चावल", "பழுப்பு அரிசி", "ಬ್ರೌನ್ ಅಕ್ಕಿ", "బ్రౌన్ రైస్", "বাদামি চাল"],
    "wheat flour": ["wheat flour", "गेहूं का आटा", "கோதுமை மா", "ಗೋಧಿ ಹಿಟ್ಟು", "గోధుమ పిండి", "গমের আটা"],
    "whole wheat flour": ["whole wheat flour", "संपूर्ण गेहूं का आटा", "முழு கோதுமை மா", "ಪೂರ್ಣ ಗೋಧಿ ಹಿಟ್ಟು", "పూర్తి గోధుమ పిండి", "সম্পূর্ণ গমের আটা"],
    "rice flour": ["rice flour", "चावल का आटा", "அரிசி மாவு", "ಅಕ್ಕಿ ಹಿಟ್ಟು", "బియ్యం పిండి", "চালের আটা"],
    "rava": ["rava", "रवा", "ரவை", "ರವೆ", "రవ్వ", "রব্বা"],
    "cornflour": ["cornflour", "मकई का आटा", "சோளம் மாவு", "ಮೆಕ್ಕೆಜೋಳ ಹಿಟ್ಟು", "మొక్కజొన్న పిండి", "ভুট্টার আটা"],
    "jowar": ["jowar", "ज्वार", "சோளம்", "ಜೋಳ", "జొన్న", "জোয়ার"],
    "bajra": ["bajra", "बाजरा", "கம்பு", "ಸಜ್ಜೆ", "సజ్జ", "বাজরা"],
    "oats": ["oats", "जई", "ஓட்ஸ்", "ಓಟ್ಸ್", "ఓట్స్", "ওটস"],
    "onion": ["onion", "प्याज", "வெங்காயம்", "ಈರುಳ್ಳಿ", "ఉల్లిపాయ", "পেঁয়াজ"],
    "tomato": ["tomato", "टमाटर", "தக்காளி", "ಟೊಮೆಟೊ", "టమాట", "টমেটো"],
    "potato": ["potato", "आलू", "உருளைக்கிழங்கு", "ಅಲೂಗೆಡ್ಡೆ", "బంగాళాదుంప", "আলু"],
    "garlic": ["garlic", "लहसुन", "பூண்டு", "ಬೆಳ್ಳುಳ್ಳಿ", "వెల్లులి", "রসুন"],
    "ginger": ["ginger", "अदरक", "இஞ்சி", "ಶುಂಠಿ", "అల్లం", "আদা"],
    "carrot": ["carrot", "गाजर", "காரட்", "ಗಾಜರ", "కారెట్", "গাজর"],
    "cauliflower": ["cauliflower", "फूलगोभी", "கோசு", "ಹೂಕೋಸು", "పూవు కోసు", "ফুলকপি"],
    "broccoli": ["broccoli", "ब्रोकली", "ப்ரோக்கொலி", "ಬ್ರೋಕೋಲಿ", "బ్రోకలీ", "ব্রকোলি"],
    "cabbage": ["Cabbage", "पत्ता गोभी", "முட்டைகோசு", "ಎಲೆಕೋಸು", "గోబీ ఆకులు", "বাঁধাকপি"],
    "spinach": ["Spinach", "पालक", "கீரை", "ಪಾಲಕ್", "పాలకూర", "পালং শাক"],
    "methi": ["Fenugreek", "मेथी", "வெந்தயம்", "ಮೆಂತ್ಯ", "మెంతి", "মেথি"],
    "palak": ["Spinach", "पालक", "பசலைக் கீரை", "ಪಾಲಕ್", "పాలకూర", "পালং শাক"],
    "bottle gourd": ["Bottle Gourd", "लौकी", "சுரைக்காய்", "ಸೋರಕಾಯಿ", "సొరకాయ", "লাউ"],
    "pumpkin": ["Pumpkin", "कद्दू", "பரங்கிக்காய்", "ಕುಂಬಳಕಾಯಿ", "గుమ్మడికాయ", "কুমড়ো"],
    "brinjal": ["Brinjal", "बैंगन", "கத்தரிக்காய்", "ಬದನೆಕಾಯಿ", "వంకాయ", "বেগুন"],
    "okra": ["Okra", "भिंडी", "வெண்டை", "ಬೆಂಡೆಕಾಯಿ", "బెండకాయ", "ঢেঁড়স"],
    "bell peppers": ["Bell Peppers", "शिमला मिर्च", "குடைமிளகாய்", "ಶಿಮ್ಲಾ ಮೆಣಸಿನಕಾಯಿ", "శిమ్లా మిర్చి", "ক্যাপসিকাম"],
    "beans": ["Beans", "फली", "பயத்தம்", "ಹುರಳಿಕಾಯಿ", "బీన్స్", "শিম"],
    "peas": ["Peas", "मटर", "பட்டாணி", "ಬಟಾಣಿ", "పచ్చి బటాణీ", "মটর"],
    "mushrooms": ["Mushrooms", "कुम्भी", "காளான்", "ಅಣಬೆ", "కాళ్లు", "মাশরুম"],
    "radish": ["Radish", "मूली", "முள்ளங்கி", "ಮೂಲಂಗಿ", "ముల్లంగి", "মূলা"],
    "turnip": ["Turnip", "शलजम", "சிகப்புக்கிழங்கு", "ಶಲಗಂ", "శలగము", "শালগম"],
    "beets": ["Beets", "चुकंदर", "குமிழ்கிழங்கு", "ಬೀಟ್ರೂಟ್", "బీట్‌రూట్", "বিট"],
    "coriander leaves": ["Coriander Leaves", "धनिया पत्तियां", "கொத்தமல்லி இலைகள்", "ಕೊತ್ತಂಬರಿ ಸೊಪ್ಪು", "కొత్తిమీర", "ধনেপাতা"],
    "mint leaves": ["Mint Leaves", "पुदीना पत्तियां", "புதினா இலைகள்", "ಪುದೀನಾ ಎಲೆ", "పుదీనా ఆకులు", "পুদিনা পাতা"],
    "curry leaves": ["Curry Leaves", "कड़ी पत्ता", "கருவேப்பிலை", "ಕರಿಬೇವು", "కరివేపాకు", "কারি পাতা"],
    "lemon": ["Lemon", "नींबू", "எலுமிச்சை", "ನಿಂಬೆ", "నిమ్మకాయ", "লেবু"],
    "lime": ["Lime", "नींबू", "சிறு எலுமிச்சை", "ಲೈಮ್", "లైమ్", "লেবু"],
    "milk": ["Milk", "दूध", "பால்", "ಹಾಲು", "పాలు", "দুধ"],
    "curd": ["Curd", "दही", "மோர்", "ಮಜ್ಜಿಗೆ", "పెరుగు", "দই"],
    "ghee": ["Ghee", "घी", "நெய்", "ತೂಪ್ಪ", "నెయ్యి", "ঘি"],
    "butter": ["Butter", "मक्खन", "வெண்ணெய்", "ಬೆಣ್ಣೆ", "వెన్న", "মাখন"],
    "paneer": ["Paneer", "पनीर", "பனீர்", "ಪನೀರ್", "పనీర్", "পনির"],
    "cheese": ["cheese", "चीज", "சீஸ்", "ಚೀಸ್", "చీజ్", "চিজ"],
    "almonds": ["almonds", "बादाम", "முந்திரி", "ಬಾದಾಮಿ", "బాదం", "বাদাম"],
    "cashews": ["Cashews", "काजू", "முந்திரிப்பருப்பு", "ಗೋಡಂಬಿ", "కాజూ", "কাজু"],
    "pistachios": ["Pistachios", "पिस्ता", "பிஸ்தா", "ಪಿಸ್ತು", "పిస్తా", "পিস্তাচিও"],
    "walnuts": ["Walnuts", "अखरोट", "அக்ரோட்", "ಅಕ್ರೋಟ್", "అక్రోట్", "আখরোট"],
    "raisins": ["Raisins", "किशमिश", "உலர்ந்த திராட்சை", "ಒಣ ದ್ರಾಕ್ಷಿ", "ఎండుద్రాక్ష", "কিশমিশ"],
    "dates": ["Dates", "खजूर", "பேரிச்சம்பழம்", "ಖರ್ಜೂರ", "ఖర్జూరం", "খেজুর"],
    "dried apricots": ["Dried Apricots", "सूखे खुबानी", "உலர் அப்ரிகோட்", "ಒಣ ಹಣ್ಣು", "ఎండిన ఖర్జూరాలు", "শুকনো এপ্রিকট"],
    "dried figs": ["Dried Figs", "सूखे अंजीर", "உலர்ந்த அத்திப்பழம்", "ಒಣ ಅಂಜೂರ", "ఎండిన అంజీరు", "শুকনো ডুমুর"],
    "oil": ["Oil", "तेल", "எண்ணெய்", "ಎಣ್ಣೆ", "నూనె", "তেল"],
    "salt": ["Salt", "नमक", "உப்பு", "ಬೆಲ್ಲು", "ఉప్పు", "লবণ"],
    "sugar": ["Sugar", "चीनी", "சர்க்கரை", "ಸಕ್ಕರೆ", "చక్కెర", "চিনি"],
    "jaggery": ["Jaggery", "गुड़", "வெல்லம்", "ಬೆಲ್ಲ", "బెల్లం", "গুড়"],
    "honey": ["Honey", "शहद", "தேன்", "ಜೇನು", "తేనె", "মধু"],
    "vinegar": ["Vinegar", "सिरका", "வினிகர்", "ವಿನೆಗರ್", "వినెగర్", "ভিনেগার"],
    "baking soda": ["Baking Soda", "सोडा", "சோடா", "ಬೇಕಿಂಗ್ ಸೋಡಾ", "బేకింగ్ సోడా", "সোডা"],
    "baking powder": ["Baking Powder", "बेकिंग पाउडर", "பேக்கிங் பவுடர்", "ಬೇಕಿಂಗ್ ಪೌಡರ್", "బేకింగ్ పౌడర్", "বেকিং পাউডার"],
    "food color": ["Food Color", "खाद्य रंग", "உணவு நிறம்", "ಆಹಾರ ಬಣ್ಣ", "ఆహార రంగు", "খাদ্য রং"],
    "saffron": ["Saffron", "केसर", "குங்குமப்பூ", "ಕುಂಕುಮಪು", "కుంకుమపువ్వు", "জাফরান"],
    "green cardamom pods": ["Green Cardamom Pods", "हरी इलायची", "பச்சை ஏலக்காய்", "ಹಸಿರು ಏಲಕ್ಕಿ", "పచ్చ ఏలకులు", "সবুজ এলাচ"],
    "black cardamom pods": ["Black Cardamom Pods", "काली इलायची", "கருப்பு ஏலக்காய்", "ಕಪ್ಪು ಏಲಕ್ಕಿ", "నల్ల ఏలకులు", "কালো এলাচ"],
    "poppy seeds": ["Poppy Seeds", "खसखस", "கசகசா", "ಗಸಗಸೆ", "గసగసాలు", "পোস্ত"],
    "flax seeds": ["Flax Seeds", "अलसी के बीज", "ஆளி விதைகள்", "ಅಗಸೆ ಬೀಜ", "ఆవాలువిత్తనాలు", "তিসির বীজ"],
    "sesame seeds": ["Sesame Seeds", "तिल", "எள் விதைகள்", "ಎಳ್ಳು", "నువ్వులు", "তিল"],
    "fish": ["fish", "मछली", "மீன்", "ಮೀನು", "మీనం", "মাছ"],
    "coconut flakes": ["Coconut Flakes", "नारियल के गुच्छे", "தேங்காய் துருவல்", "ತರುಟು ತೆಂಗಿನಕಾಯಿ", "కోబ్బరి తురుము", "নারকেল কুঁচি"],
    "coconut milk": ["Coconut Milk", "नारियल का दूध", "தேங்காய் பால்", "ತೆಂಗಿನ ಹಾಲು", "కొబ్బరిపాలు", "নারকেল দুধ"],
    "mustard paste": ["Mustard Paste", "सरसों का पेस्ट", "கடுகு பேஸ்ட்", "ಸಾಸಿವೆ ಪೇಸ್ಟ್", "ఆవపేస్ట్", "সরষে পেস্ট"],
    "tomato paste": ["Tomato Paste", "टमाटर का पेस्ट", "தக்காளி பேஸ்ட்", "ಟೊಮೆಟೊ ಪೇಸ್ಟ್", "టమోటా పేస్ట్", "টমেটো পেস্ট"],
    "chilli flakes": ["Chilli Flakes", "मिर्च के गुच्छे", "மிளகாய் துண்டுகள்", "ಮೆಣಸಿನ ಹುಡಿ", "మిరపకాయల పొడి", "মরিচের ফ্লেক্স"],
    "chicken stock": ["Chicken Stock", "चिकन स्टॉक", "கோழி சதுரம்", "ಚಿಕನ್ ಸ್ಟಾಕ್", "చికెన్ స్టాక్", "চিকেন স্টক"],
    "vegetable stock": ["Vegetable Stock", "सब्जी स्टॉक", "காய்கறி சதுரம்", "ತರುಟು ತರಕಾರಿ", "కూరగాయల స్టాక్", "সবজি স্টক"],
    "rice": ["rice", "चावल", "அரிசி", "ಅಕ್ಕಿ", "బియ్యం", "চাল"]
}
# Database setup for user authentication






# Registration Route

# Index Route (Landing Page after login)
@app.route('/')
def home():
    return render_template('test.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if user_message:
        response = chat_session.send_message(user_message)
        model_response = response.text
        print(f"Model response: {user_message}")
        print(f"Model response: {model_response}")
        return jsonify({"response": model_response})
    return jsonify({"error": "No message received."}), 400

@app.route('/get-ingredients/<ingredient>', methods=['GET'])
def get_ingredients(ingredient):
    ingredient_data = common_ingredients.get(ingredient.lower())
    if ingredient_data:
        return jsonify({"ingredient_translations": ingredient_data})
    return jsonify({"error": "Ingredient not found."}), 404

# Start the Flask application
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)