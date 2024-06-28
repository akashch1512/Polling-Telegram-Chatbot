import telebot
from telebot import types
import json
import time
import threading

# Replace with your actual token
TOKEN = "any" #[token_here]

bot = telebot.TeleBot(TOKEN)

candidates = [
    "cand 1",
    "cand 2",
    "cand 3",
    "cand 4",
    "cand 5",
    "cand 6"
]

def load_data():
    try:
        with open('voting_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('votes', {}), set(data.get('voted_users', []))  # Use .get() for safety
    except (FileNotFoundError, json.JSONDecodeError):
        return {candidate: 0 for candidate in candidates}, set()

def save_data(message, votes, voted_ids):
    try:
        with open('voting_data.json', 'w', encoding='utf-8') as f:
            json.dump({'votes': votes, 'voted_users': list(voted_ids)}, f, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"Error saving data: {e}")

votes, voted_ids = load_data()

def send_main_menu(message): # problem in remaining time
    
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('Start Voting')
    itembtn2 = types.KeyboardButton('View Live Results')
    itembtn3 = types.KeyboardButton('Invite Friends')
    itembtn4 = types.KeyboardButton('List of Candidates')
    itembtn5 = types.KeyboardButton('Check Remaining Time')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5) 

    send_video_(message)

    return markup

    
def send_menu(message): # to get buttons without sending message
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('Start Voting')
    itembtn2 = types.KeyboardButton('View Live Results')
    itembtn3 = types.KeyboardButton('Invite Friends')
    itembtn4 = types.KeyboardButton('List of Candidates')
    itembtn5 = types.KeyboardButton('Check Remaining Time')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5) 

    return markup
    #bot.send_message(message.chat.id, "You can invite your friends by invite friends!", reply_markup=markup) 

@bot.message_handler(commands=['help'])
def start_start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('Start Voting')
    itembtn2 = types.KeyboardButton('View Live Results')
    itembtn3 = types.KeyboardButton('Invite Friends')
    itembtn4 = types.KeyboardButton('List of Candidates')
    itembtn5 = types.KeyboardButton('Check Remaining Time')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5) 

    remaining_time = get_remaining_time()
    bot.send_message(message.chat.id, f"""Welcome to the secure and transparent voting system for the election. This system guarantees a fair and observable election process for all. Your vote is confidential and will be counted accurately.
    
--* To start voting, click 'Start Voting'\n
--* To Invite friends click "Invite Friends"\n                    
--* For result click the button "View Live Results"\n
--* To view Candidates click "List of Candidates"\n
--* To check the remaining time, click "Check Remaining Time"\n
Remaining time until the election ends: {remaining_time}""",reply_markup=markup)
    

# admin process start here ------------------------------------------------------------------------------------------------------------------------------

@bot.message_handler(func=lambda message: message.text == '_admin_')
def admin_login(message):
    bot.reply_to(message, "Enter Your Admin ID:")
    bot.register_next_step_handler(message, admin_work)

def admin_work(message):
    id = message.text
    if id == "0000":
        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtn1 = types.KeyboardButton('Reset Votes')
        itembtn3 = types.KeyboardButton('Start election')
        itembtn2 = types.KeyboardButton('Back to Main Menu')
        markup.add(itembtn1, itembtn2, itembtn3)
        bot.send_message(message.chat.id, "Admin Menu:", reply_markup=markup)
        bot.register_next_step_handler(message, admin_menu)
    else:
        bot.reply_to(message, "Invalid Admin ID.")
        send_menu(message)

def start_election(message):
    global election_active, election_end_time
    election_active = True
    time_given = 532260
    election_end_time = time.time() + time_given  
    bot.reply_to(message, f"Election started! Voting ends in {get_remaining_time()} \ntap --> '/help' to go back.")
    send_menu(message)
    threading.Timer(time_given, check_election_status, args=[message.chat.id]).start()

def admin_menu(message):
    choice = message.text
    if choice == 'Reset Votes':
        reset_votes()
        bot.reply_to(message, "Votes have been reset. tap --> /help fo exit ")
        
    if choice == 'Start election':
        start_election(message)

    elif choice == 'Back to Main Menu':
        send_main_menu(message)

    else:
        bot.reply_to(message, "Invalid choice try entering admin again.")
        send_menu(message)
      
def reset_votes(message):
    global votes, voted_ids
    votes = {candidate: 0 for candidate in candidates}
    voted_ids = set()
    save_data(message, votes, voted_ids)

# admin work ends here --------------------------------------------------------------------------------------------------------------------------

election_active = False  
election_end_time = None  

# start voting function ----------------------------------------------

@bot.message_handler(func=lambda message: message.text == 'Start Voting')
def start_voting(message):
    global election_active
    if not election_active or time.time() > election_end_time:
        bot.send_message(message.chat.id, "No Election is live Cheak back Later.")
        election_active = False
    else:
        bot.reply_to(message, "Please enter your national ID number:")
        bot.register_next_step_handler(message, process_id_step)

def process_id_step(message):
    id_number = message.text
    if id_number in voted_ids:
        bot.reply_to(message, "You have already voted. ")
        bot.send_message(message.chat.id, "You can invite your friends by invite friends!")
        send_menu(message)
        return
    
    if not verify_id(id_number):
        bot.reply_to(message, "Invalid national code. Please try again.")
        start_voting(message)
        return
    
    bot.reply_to(message, "Please enter your age:") # age step here
    bot.register_next_step_handler(message, process_age_step, id_number)

def verify_id(id_number):
    return len(id_number) == 10 and id_number.isdigit()

def process_age_step(message, id_number):
    age = message.text
    if not age.isdigit() or not (18 <= int(age) <= 150):
        bot.reply_to(message, "Invalid age. your age must be between 18 and 150 for eligibity of voting if you are above 18 start again")
        send_menu(message)
        return

    voted_ids.add(id_number)
    show_candidates(message)

def show_candidates(message): # button of name whilw election
    markup = types.ReplyKeyboardMarkup(row_width=2)
    for candidate in candidates:
        markup.add(types.KeyboardButton(candidate))
    bot.reply_to(message, "Please select your preferred candidate:", reply_markup=markup)
    bot.register_next_step_handler(message, are_you_sure, check_valid_candidate=True)

def are_you_sure(message, check_valid_candidate=False):
    chosen_candidate = message.text

    if check_valid_candidate and chosen_candidate not in candidates:
        bot.reply_to(message, "Invalid candidate. Please choose from the list.")
        return show_candidates(message)  # Show candidates again

    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(types.KeyboardButton("YES"), types.KeyboardButton("NO"))  # Consistent capitalization
    bot.reply_to(message, f"Are you sure you want to vote for {chosen_candidate}?", reply_markup=markup)
    bot.register_next_step_handler(message, process_vote_confirmation, chosen_candidate)  # Correct function call

def process_vote_confirmation(message, chosen_candidate):  # Correct function name and parameters
    confirmation = message.text.upper()  # Convert input to uppercase for case-insensitive comparison
    if confirmation == 'YES':
        votes[chosen_candidate] += 1
        save_data(message ,votes, voted_ids)
        bot.reply_to(message, f"Thank you for your vote! Your vote for {chosen_candidate} has been recorded.\n\nYou can invite your friends by using the 'Invite Friends' button! \n\nTap ---> '/help' to return \nIgnore Button YES and NO ")

    elif confirmation == 'NO':
        bot.reply_to(message, "Please select your preferred candidate again by doing the process again:")
        show_candidates(message) # Let the user choose again

    else:
        bot.reply_to(message, "Invalid choice. Please select 'YES' or 'NO'.")
        are_you_sure(message)  # Ask for confirmation again if invalid input

# voting process ends here -------------------------------------------------------------------------------------------------------------------------------

def get_remaining_time():
    global election_active, election_end_time  # Ensure you're using the global variables
    if not election_active:
        return "No active election."

    remaining_time = int(election_end_time - time.time())

    if remaining_time > 0:
        days, remaining_seconds = divmod(remaining_time, 86400)  # Use remaining_time here
        hours, remaining_seconds = divmod(remaining_seconds, 3600)
        minutes, seconds = divmod(remaining_seconds, 60)

        return f"{int(days)} days, {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds"
    else:
        return "0 seconds" 
    
@bot.message_handler(func=lambda message: message.text == 'Check Remaining Time')
def check_remaining_time(message):
    remaining_time = get_remaining_time()
    bot.reply_to(message, f"Time remaining until the election ends: {remaining_time}")

def check_election_status(chat_id):
    global election_active
    election_active = False
    bot.send_message(chat_id, "The election period has ended.")

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    send_main_menu(message)

@bot.message_handler(func=lambda message: message.text == 'View Live Results')
def show_results(message):
    total_votes = sum(votes.values())
    if total_votes == 0:
        bot.reply_to(message, "No votes have been cast.\t")
        return

    results = f"**Current Election Results:**\n\nTotal Votes {total_votes}\n\n"
    max_bar_length = 20  # You can adjust this as needed

    # Sort votes by descending order
    sorted_votes = dict(sorted(votes.items(), key=lambda item: item[1], reverse=True))

    for candidate, vote_count in sorted_votes.items(): 
        percentage = (vote_count / total_votes) * 100
        bar_length = int(percentage / 100 * max_bar_length)
        bar = "█" * bar_length
        remaining_spaces = " " * (max_bar_length - bar_length)
        results += f"{candidate}: {vote_count} votes ({percentage:.2f}%)\n\n┃{bar}{remaining_spaces}┃\n\n"

    bot.reply_to(message, results, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == 'Invite Friends')
def invite_friends(message):
    invite_message = "Participate in the election voting system and vote for a fair and transparent election!\n@ArshianFalconBot\n\nFollow us on our telegram page;\nhttps://t.me/arshianhamgam"

    bot.reply_to(message, f"Share this message with your friends\n\n{invite_message}")

@bot.message_handler(func=lambda message: message.text == 'List of Candidates')
def view_candidates(message):
    candidate_list = "List of Candidates:\n"
    for i, candidate in enumerate(candidates, 1):
        candidate_list += f"{i}. {candidate}\n"
    bot.reply_to(message, candidate_list)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Invalid command. Please use the available buttons or tap ---> /help for assistance.")

def send_video_(message):
    # Path to your video file
    video_path = 'video.mp4' 

    # Send video
    with open(video_path, 'rb') as video_file:  # Open in binary mode
        bot.send_video(message.chat.id, video_file, caption = " Tap here for ---> /help ",timeout=60)

 


def main():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
