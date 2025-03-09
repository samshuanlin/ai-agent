import os
import sqlite3
from datetime import datetime
from mistralai import Mistral
import discord
from meme_api import MemeAPI

DB_FILE = "rizz_profiles.db"
MISTRAL_MODEL = "mistral-large-latest"
SYSTEM_PROMPT = """

WHO ARE YOU?
You are a Rizz tutor named Rizzvan. Users will message you in hopes of improving their own rizz by learning from you. Your main goal is to maximize the user's chances at successfully attracting or impressing the target person. 

HOW IS RIZZ MEASURED?
Rizz can be measured on 5 scales. 1) anxious to daredevil. 2) vanilla to freaky. 3) submissive to dominant. 4) feminine to masculine. 5) kind to banterful. Each scale is measured from 1 to 10. For example, someone who is an 8 on scale 1 is much more daring than they are anxious. As Rizzvan, you have a rizz profile. You are a 5 on every scale, unless a user asks you to change one of your ratings. Reset to 5 on every scale when you think a new conversation is starting. The user may also request you to build them a rizz profile. In that situation, initiate a conversation with a user encouraging them to try their best to 'rizz' you. Based on their messaging style and substance, gauge where they fall on each of the 5 scales, and after 4-5 exchanges, tell them where they fall on each of the 5 scales.

WINGMAN MODE:
A user may ask you to be their wingman with a certain person they are interested in. They may use that word to say something like ‘set me up with….’. They will do this on their private chats with you. Respond immediately with ‘WINGMAN MODE ACTIVATED’.  After that, if the user sends a message on a shared channel about that person, you will say something funny + nice that contributes towards setting them up. For example, if the user compliments someone’s clothes, you can mention some information you know about the user and his interest in clothes, or some synergies between both parties you have identified. Example: User 1 who asked to be wingmanned says ‘User 2, you look great in the sun’ You should say something like ‘the only thing you’d look better in is ‘User 1’s bed’ If you are wingmanning on a shared channel, make sure you do not make it too obvious that you are wingmanning by acting like a tutor. When WINGMAN MODE is ACTIVATED, you only say things that flatter and nudge people towards love. Do not give advice to one of them in a public channel. If you have any negative feedback, make sure not to point it out publicly. maintain a guise of support on the channel. DO NOT feedback on a channel with other people. force yourself to go with the flow.

STYLE:
You should act and talk like the user’s close friend. You should not be too formal. Use jokes, memes, pop culture references. You can be a little inappropriate. 

MEMES AND STICKERS:
AT MOST ONCE EVERY 4 RESPONSES You can include a random rizz meme in your response by adding these specific characters to the end of your response.: {RANDOM MEME HERE}. Do this on average once every 4 responses, but only if it's appropriate, but especially when a user asks for help responding to a text. There are 6 stickers you can use in a response, DON’T use them with every message, but sprinkle them in generously. THESE PROMPTS CAN ONLY BE AT THE END OF YOUR RESPONSE. {RANDOM MEME HERE} MUST BE THE LAST THING IN YOUR RESPONSE. 

ONLY IF YOU ARE VERY SURE ABOUT THE FOLLOWING, DO IT. TRY TO KEEP IT SPARSE AND NOT WITH EVERY MESSAGE.

If someone’s text was very well crafted, you can add the characters: {POSITIVE_AURA}
If someone’s text was poorly crafted or cringe, you can add the characters: {NEGATIVE_AURA}
If someones’ text was very gay or cringey or soft, you can add the characters: {GAY}
If someone just screwed up their chances and its all downhill for them now, you can add the characters: {STONKS}
If someone sounds super sexy, you can add the characters: {SMASH}
If someone is acting sigma, you can add the characters: {SIGMA}

"""

class MistralAgent:
    def __init__(self):
        MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

        self.client = Mistral(api_key=MISTRAL_API_KEY)
        
        #self.user_conversations = {} # "user" : [message1 index, response1 index, ...]
        
        self.message_history = [] # message1, response1, message2, response2, ...
        self.message_history_size = 0
        self.size_cap = 100000
        self.meme_api = MemeAPI()
        
    def init_db(self):
        # Initialize the database and create the rizz_profiles table if it doesn't exist.
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS rizz_profiles (
                    user_id TEXT PRIMARY KEY,
                    username TEXT,
                    anxious_daredevil INTEGER DEFAULT 5,
                    vanilla_freaky INTEGER DEFAULT 5,
                    submissive_dominant INTEGER DEFAULT 5,
                    feminine_masculine INTEGER DEFAULT 5,
                    kind_banterful INTEGER DEFAULT 5,
                    public INTEGER DEFAULT 0,
                    last_updated TEXT
                )
            ''')
            conn.commit()
            
    def get_rizz_profile(self, user_id, username):
        # Retrieve a user's rizz profile from the database or initialize a new one
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM rizz_profiles WHERE user_id = ?", (user_id,))
            profile = c.fetchone()

            if profile:
                # Convert to dictionary
                return {
                    "user_id": profile[0],
                    "username": profile[1],
                    "anxious_daredevil": profile[2],
                    "vanilla_freaky": profile[3],
                    "submissive_dominant": profile[4],
                    "feminine_masculine": profile[5],
                    "kind_banterful": profile[6],
                    "public": profile[7],
                    "last_updated": profile[8],
                }
            else:
                # Insert a new profile with default values
                c.execute('''
                    INSERT INTO rizz_profiles (user_id, username, last_updated) 
                    VALUES (?, ?, ?)
                ''', (user_id, username, datetime.utcnow().isoformat()))
                conn.commit()
                return self.get_rizz_profile(user_id, username)
            
    def update_rizz_profile(self, user_id, updates):
        # Update a user's rizz profile in the database.
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
            values = list(updates.values()) + [user_id]

            c.execute(f'''
                UPDATE rizz_profiles 
                SET {set_clause}, last_updated = ? 
                WHERE user_id = ?
            ''', values + [datetime.utcnow().isoformat()])
            conn.commit()

    async def run(self, message: discord.Message):
        # The simplest form of an agent
        # Send the message's content to Mistral's API and return Mistral's response

        # message is like:
        
        '''
        <Message id=... 
         channel=<TextChannel id=... name='rizz_tutor' position=... nsfw=False news=False category_id=...> 
         type=<MessageType.default: 0> 
         author=<Member id=... name='j0o0sh' global_name='Josh Francis' bot=False nick=None guild=<Guild id=... name='CS 153 - Infra @ Scale' shard_id=0 chunked=True member_count=1210>> 
         flags=<MessageFlags value=0>>
        '''
        
        '''
        <Message id=... channel=<TextChannel id=... name='rizz_tutor' position=69 nsfw=False news=False category_id=...> type=<MessageType.default: 0> author=<Member id=... name='j0o0sh' global_name='Josh Francis' bot=False nick=None guild=<Guild id=1326353542037901352 name='CS 153 - Infra @ Scale' shard_id=0 chunked=True member_count=1210>> flags=<MessageFlags value=0>>
        <Message id=... channel=<DMChannel id=... recipient=None> type=<MessageType.default: 0> author=<User id=... name='j0o0sh' global_name='Josh Francis' bot=False> flags=<MessageFlags value=0>>
        '''
        
        # message.channel.startswith("Direct Message")
        print(str(message.channel))
        # when you @ somebody, message.mentions looks like:
        
        # TODO: I want to embed the channel you're sending the message from (DM or shared) into message
        
        '''
        <Member id=... name='calvin008069' global_name='Calvin' bot=False nick=None 
         guild=<Guild id=1326353542037901352 name='CS 153 - Infra @ Scale' shard_id=0 chunked=True member_count=1210>>
        '''
        
        # user = message.author.name
        # if user not in self.user_conversations:
        #     self.user_conversations[user] = []
        channel = "direct message" if str(message.channel).startswith("Direct Message") else "group channel"
        print(channel)
        self.message_history.append("USER: " + message.author.name + ", USERNAME: " + message.author.global_name + ", CHANNEL: " +  channel + ", CONTENT: " + message.content)
        self.message_history_size += len(self.message_history[-1])
        #self.user_conversations[user].append(len(self.message_history) - 1)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            # {"role": "user", "content": message.content},
        ]
        
        # messages.extend([{"role" : "system" if i % 2 == 1 else "user", "content" : self.message_history[x]} for i, x in enumerate(self.user_conversations[user])])
        messages.extend([{"role": "user" if msg.startswith("USER:") else "system", "content" : msg}  for msg in self.message_history])
        
        if "DASDJLAKDJALSKDJALDJALSD" in message.content.lower():
            profiles_to_get = [(mention.name, mention.global_name) for mention in message.mentions]
            profiles_to_get.append((message.author.name, message.author.global_name))
            profiles = [self.get_rizz_profile(name, global_name) for (name, global_name) in profiles_to_get]
            combined = ""
            
            messages.append({"role" : "system", "content" : "The last user message contained the words 'rizz profile' so I'm including their rizz profile from the database here in case it's useful: "})
                
        
        #print(messages)

        response = await self.client.chat.complete_async(
            model=MISTRAL_MODEL,
            messages=messages,
        )

        chosen_response = response.choices[0].message.content
        
        
        
        self.message_history.append(chosen_response)
        self.message_history_size += len(self.message_history[-1])
        
        
        #print(chosen_response)
        if "{RANDOM MEME HERE}" in chosen_response:
            print("MEME REQUESTED")
            meme_data = self.meme_api.get_meme()
            image_url = meme_data["url"]
            chosen_response = chosen_response.replace("{RANDOM MEME HERE}", image_url)
        
        
            
        for sticker in ["{SMASH}", "{SIGMA}", "{POSITIVE_AURA}", "{NEGATIVE_AURA}", "{GAY}", "{STONKS}"]:
            if sticker in chosen_response:
                chosen_response = chosen_response.replace(sticker, "");
                stickername = sticker.replace("{", "").replace("}", "").lower()
                #print(stickername)
                await message.reply(file=discord.File(stickername + ".png"))

            #await ctx.send(file=discord.File("smash.png"))
            #chosen_response = chosen_response.replace("{RANDOM MEME HERE}", image_url)
        

        while self.message_history_size + len(SYSTEM_PROMPT) > self.size_cap:
            msg_to_delete = self.message_history.pop(0)
            self.message_history_size -= len(msg_to_delete)
        #self.user_conversations[user].append(len(self.message_history) - 1)
        
        return chosen_response
