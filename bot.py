import os
import time
import random
import telebot
from telebot import types
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# --- Configuration ---
# ⚠️ Put your Telegram ID number below
ADMIN_ID = 7667102081 

BOT_TOKEN = "8318313561:AAEAwJ3bVmmtQJjN2_Orxd-6zl1H6sqUaLY"
bot = telebot.TeleBot(BOT_TOKEN)

driver = None

def get_driver():
    """Function to start driver and bypass anti-bot security"""
    global driver
    if driver is None:
        options = Options()
        options.add_argument("--headless=new")  # Modern headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")  # Disable GPU for GitHub Actions stability
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--window-size=1920,1080")  # High resolution for desktop layout
        
        # Page load strategy 'eager' (browser won't hang for heavy images)
        options.page_load_strategy = 'eager'
        
        # --- Anti-bot security bypass settings ---
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        options.add_argument("--user-data-dir=./whatsapp_session")
        
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(120)
        
        # Remove Selenium robot flag from inside the browser
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
    return driver

# Helper function to type extremely slowly like a human
def human_type(element, text):
    element.clear()
    for character in text:
        element.send_keys(character)
        time.sleep(random.uniform(0.25, 0.55))  # Extremely slow normal keyboard typing speed

# Helper function to scroll browser like a human
def human_scroll(web_driver):
    try:
        web_driver.execute_script("window.scrollTo(0, 200);")
        time.sleep(2.0)
        web_driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1.5)
    except:
        pass

# Function to send live diagnostic report and real screenshot on failure
def send_failure_diagnostic(message, error_msg, web_driver):
    try:
        # Take a picture of the current state of the GitHub virtual browser
        web_driver.save_screenshot("diagnostic.png")
        page_title = web_driver.title
        current_url = web_driver.current_url
        
        report = (
            "🔍 **[AI Deep Diagnostic Report]**\n\n"
            f"❌ **Error Type:** `{error_msg}`\n"
            f"🌐 **Link:** {current_url}\n"
            f"📄 **Title:** {page_title}\n\n"
            "🤖 **AI Analysis & Possible Solutions:**\n"
            "1. The browser might be stuck on the WhatsApp loading page.\n"
            "2. Session refresh or connection complications may have occurred.\n\n"
            "👇 A real-time screenshot of what is currently visible in the browser is sent below:"
        )
        with open("diagnostic.png", "rb") as diag_file:
            bot.send_photo(message.chat.id, diag_file, caption=report, parse_mode="Markdown")
    except Exception as diag_e:
        bot.send_message(message.chat.id, f"❌ Failed to generate AI diagnostic report: {diag_e}")

# 1. Start command (Buttons will appear without delay)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_developer = types.KeyboardButton("👤 Developer")
    btn_check_ws = types.KeyboardButton("🔍 Check Number")
    markup.add(btn_developer, btn_check_ws)
    
    bot.send_message(
        message.chat.id, 
        "Welcome to the WhatsApp Number Checker Bot! Use the buttons below:", 
        reply_markup=markup
    )

# 2. Secure admin login command (Link code generation)
@bot.message_handler(commands=['login'])
def admin_login(message):
    # Verify ID
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Sorry, this command is reserved for the bot admin only.")
        return

    msg = bot.send_message(
        message.chat.id, 
        "📱 Please send your WhatsApp number with country code (e.g., 923XXXXXXXXX):\n"
        "(This number will be used to connect or link your bot)"
    )
    bot.register_next_step_handler(msg, process_admin_phone)

# Function to process phone number and get link code from WhatsApp
def process_admin_phone(message):
    raw_input = message.text.strip().replace(" ", "")
    
    # AI based parsing and international formatting (+92XXXXXXXXX)
    if raw_input.startswith("0"):
        formatted_num = "+92" + raw_input[1:]
    elif raw_input.startswith("92"):
        formatted_num = "+" + raw_input
    elif raw_input.startswith("+"):
        formatted_num = raw_input
    else:
        formatted_num = "+92" + raw_input
        
    bot.send_message(message.chat.id, f"⏳ Generating link code in international format ({formatted_num}) on WhatsApp...")
    
    try:
        web_driver = get_driver()
        bot.send_message(message.chat.id, "🤖 [AI Analysis]: Chrome session started. WhatsApp page loading...")
        web_driver.get("https://web.whatsapp.com")
        
        # Wait and scroll screen like a human after page load
        time.sleep(8)
        bot.send_message(message.chat.id, "🤖 [AI Analysis]: Scrolling screen like a human...")
        human_scroll(web_driver)
        time.sleep(4)
        
        # Search for 'Link with phone number' button (specific XPath to avoid parent match)
        button_xpath = "//*[contains(text(), 'Link with phone number') or contains(text(), 'Log in with phone number') or contains(text(), 'Link with Phone Number')]"
        
        try:
            link_btn = WebDriverWait(web_driver, 90).until(
                EC.element_to_be_clickable((By.XPATH, button_xpath))
            )
            bot.send_message(message.chat.id, "🤖 [AI Analysis]: Button found. Clicking like a human...")
            time.sleep(1.5)
            
            # Double-layer click method (so click is never missed)
            try:
                link_btn.click()
            except Exception:
                web_driver.execute_script("arguments[0].click();", link_btn)
                
            bot.send_message(message.chat.id, "🤖 [AI Analysis]: Button clicked. Waiting for page transition and animation...")
            time.sleep(8)  # Giving 8 seconds like a human for page change and load
        except Exception as e:
            # Check if chat list exists (if already logged in)
            chat_list = web_driver.find_elements(By.XPATH, "//div[@id='pane-side']")
            if len(chat_list) > 0:
                bot.send_message(message.chat.id, "✅ Your WhatsApp session is already successfully logged in!")
                return
            else:
                raise e
        
        bot.send_message(message.chat.id, "🤖 [AI Analysis]: Filtering visible and active phone number input box...")
        
        # Finding the first visible and active input field
        phone_input = None
        start_input_time = time.time()
        while time.time() - start_input_time < 30:
            inputs = web_driver.find_elements(By.XPATH, "//input")
            for inp in inputs:
                if inp.is_displayed() and inp.is_enabled():
                    inp_type = inp.get_attribute("type")
                    if inp_type != "file" and inp_type != "hidden":
                        phone_input = inp
                        break
            if phone_input:
                break
            time.sleep(2)
            
        if phone_input is None:
            raise TimeoutException("Phone number input box was not found in a visible state.")
        
        # Completely delete the default number with country code
        bot.send_message(message.chat.id, "🤖 [AI Analysis]: Completely deleting the default country code via keyboard...")
        phone_input.send_keys(Keys.CONTROL + "a")
        phone_input.send_keys(Keys.BACKSPACE)
        time.sleep(1.5)
        
        # Type plus (+) sign and full number like a human
        bot.send_message(message.chat.id, f"🤖 [AI Analysis]: Typing {formatted_num} with plus (+) and country code like a human...")
        human_type(phone_input, formatted_num)
        
        # Pause for 3 seconds to review the number like a human before submitting
        time.sleep(3)
        
        # Find and click the green 'Next' button
        bot.send_message(message.chat.id, "🤖 [AI Analysis]: Clicking the green 'Next' button...")
        next_button_xpath = "//*[contains(text(), 'Next') or contains(text(), 'NEXT')]"
        try:
            next_btn = WebDriverWait(web_driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, next_button_xpath))
            )
            try:
                next_btn.click()
            except Exception:
                web_driver.execute_script("arguments[0].click();", next_btn)
        except Exception:
            # If for some reason the next button doesn't work, press enter from keyboard
            bot.send_message(message.chat.id, "🤖 [AI Analysis]: 'Next' button is not clickable, submitting by pressing Enter key...")
            phone_input.send_keys(Keys.ENTER)
            
        time.sleep(12) # Time for code to fully generate and appear on screen
        
        # Take screenshot and send window
        web_driver.save_screenshot("pairing_code.png")
        with open("pairing_code.png", "rb") as code_file:
            caption_text = (
                "🔑 You will see your 8-character link code in the middle of the image.\n\n"
                "👉 **How to link this:**\n"
                "1. Go to WhatsApp on your mobile ➡️ 3 dots on top right (or Settings) ➡️ Linked Devices ➡️ Click on Link a Device.\n"
                "2. Now click on the 'Link with phone number instead' option at the bottom.\n"
                "3. Correctly type the 8-character link code seen in the image on your mobile."
            )
            bot.send_photo(message.chat.id, code_file, caption=caption_text)
            
        bot.send_message(message.chat.id, "⏳ Waiting for you to enter the code on your mobile (I will check for 1 minute)...")
        linked = False
        for _ in range(20): # Will check for a total of 60 seconds
            time.sleep(3)
            chat_list = web_driver.find_elements(By.XPATH, "//div[@id='pane-side']")
            if len(chat_list) > 0:
                linked = True
                break
                
        if linked:
            bot.send_message(message.chat.id, "🎉 Congratulations! Your WhatsApp account has been successfully linked. Now any user can directly check numbers.")
        else:
            bot.send_message(message.chat.id, "⏱️ Linking time has expired. If it hasn't linked yet, try typing `/login` again.")
            
    except Exception as e:
        # Convert complex error messages to human-readable text
        error_msg = str(e).split("\n")[0]
        if "TimeoutException" in str(type(e)):
            error_msg = "WhatsApp page took too long to load (slow server)."
        elif "WebDriverException" in str(type(e)):
            error_msg = "Browser failed to launch in the background."
            
        # Send report with actual cause of failure and real screenshot
        send_failure_diagnostic(message, error_msg, web_driver)

# 3. General button click handler
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    if message.text == "👤 Developer":
        dev_info = (
            "👤 **Developer Information:**\n\n"
            "This automation system is built with Python for Kamboh Chatting Zone."
        )
        bot.send_message(message.chat.id, dev_info, parse_mode="Markdown")
        
    elif message.text == "🔍 Check Number":
        msg = bot.send_message(
            message.chat.id, 
            "Please send the phone number with country code (e.g., 923XXXXXXXXX):"
        )
        bot.register_next_step_handler(msg, process_phone)

# 4. Core logic for verifying number
def process_phone(message):
    phone = message.text.strip()
    if phone in ["👤 Developer", "🔍 Check Number"]:
        handle_buttons(message)
        return

    bot.send_message(message.chat.id, f"⏳ Verifying number {phone}, please wait...")
    
    try:
        web_driver = get_driver()
        url = f"https://web.whatsapp.com/send?phone={phone}"
        web_driver.get(url)
        
        # Wait for page to load
        time.sleep(10)
        
        # Check login status
        qr_present = web_driver.find_elements(By.XPATH, "//canvas[@aria-label='Scan me!']")
        chat_pane = web_driver.find_elements(By.XPATH, "//div[@id='pane-side']")
        chat_input = web_driver.find_elements(By.XPATH, "//div[@contenteditable='true']")
        
        if len(qr_present) > 0 or (len(chat_pane) == 0 and len(chat_input) == 0):
            bot.send_message(
                message.chat.id, 
                "⚠️ The bot is not linked to your WhatsApp yet!\n\n"
                "👉 Please connect the account first using the `/login` command in the bot chat."
            )
            return

        # Check for invalid number
        invalid_popup = web_driver.find_elements(By.XPATH, "//*[contains(text(), 'invalid') or contains(text(), 'Invalid')]")
        if len(invalid_popup) > 0:
            try:
                ok_button = web_driver.find_element(By.XPATH, "//button//span[contains(text(), 'OK')]")
                ok_button.click()
            except:
                pass
            bot.send_message(message.chat.id, f"❌ No WhatsApp account exists on {phone}.")
        else:
            # Check if chat input box exists (Valid number)
            if len(chat_input) > 0:
                bot.send_message(message.chat.id, f"✅ There is an active WhatsApp account on {phone}.")
            else:
                bot.send_message(message.chat.id, "⚠️ Could not be confirmed. Page took too long to load.")
                
    except Exception as e:
        print(f"Error: {e}")
        bot.send_message(message.chat.id, "❌ An internal error occurred. Please try again.")

# Start Polling
if __name__ == "__main__":
    print("Starting Telegram bot in the background...")
    bot.infinity_polling()
