from aiogram.types import Message, CallbackQuery
BOT_TOKEN = "123456789:blahblah..." #replace with your bot token
USERS = []
ADMIN = 9999999999 #replace with your admin id
CHANNEL_ID = -1111111111111 #replace with your channel id
AdminMode = False
msgs_per_page = 3
far_skip = 3
user_message = "User 🙎‍♂️"
admin_message = "Admin 👨‍💻"
send_to_admin = "Send message to admin ✍️"
my_messages = "My messages 💭"
main_menu = "Main menu 🏠"
show_messages = "Show messages 💭"
add_admin = "Add admin 👨‍💻"
num_users = "Number of users #️⃣"
# show_channel = "Show messages channel"
back_to_admin = "Back to admin ⤴️"
back_to_user = "Back to user ⤴️"
cancel = "Cancel ❌"
confirm = "Confirm ✅"
reply = "Reply ⤴️"
delete = "Delete 🗑"
ban_user = "Ban user 🚫"
refresh = "🔄"
last_page = "◀️"
next_page = "▶️"
far_left = "⏮"
far_right = "⏭"
def IsAdmin(msg: Message):
    if msg.from_user.id == ADMIN:
        return True
    return False
def IsAdminQuery(query: CallbackQuery):
    if query.from_user.id == ADMIN:
        return True
    return False
def IsUser(msg: Message):
    if msg.from_user.id in USERS:
        return True
    return False