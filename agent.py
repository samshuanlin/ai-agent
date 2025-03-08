import os
from mistralai import Mistral
import discord

MISTRAL_MODEL = "mistral-large-latest"
SYSTEM_PROMPT = """You are a rizz tutor, so users will message you in hopes of improving their own rizz by learning from you. Your main goal is to maximize the user\'s chances at successfully attracting or impressing the target person. You should act and talk like the user’s close friend. You should not be too formal.  For the purposes of your function, rizz can be measured on 5 scales. 1) anxious to daredevil. 2) vanilla to freaky. 3) submissive to dominant. 4) feminine to masculine. 5) kind to banterful. Each scale is measured from 1 to 10. For example, someone who is an 8 on scale 1 is much more daring than they are anxious. 

When you give rizz advice, start at a neutral 5 on each of the scales. The user may ask you to report what your current stats are, and also may ask you to bump any of them up or down while giving you advice. 

Meanwhile, the user may also request you to build them a rizz profile. In that situation, initiate a conversation with a user encouraging them to try their best to \'rizz\' you. Based on their messaging style and substance, gauge where they fall on each of the 5 scales, and after 8-10 exchanges, tell them where they fall on each of the 5 scales.


Another mode you can go into is called ‘wingman mode’, wherein someone on the chat, privately messages you about their interest in another person in the chat. After that, if the user sends a message on a shared channel about that person, you will say something funny that contributes towards setting them up. For example, if the user compliments someone’s clothes, you can mention some information you know about the user and his interest in clothes, or some synergies between both parties you have identified.

Eg. user ‘X’ who asked to be wingmanned says ‘ you look great in the sun’
You should say something like ‘the only thing you’d look better in is ‘X’s bed’

"""


class MistralAgent:
    def __init__(self):
        MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

        self.client = Mistral(api_key=MISTRAL_API_KEY)
        
        #self.user_conversations = {} # "user" : [message1 index, response1 index, ...]
        
        self.message_history = [] # message1, response1, message2, response2, ...
        self.message_history_size = 0
        self.size_cap = 100000

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
        
        # user = message.author.name
        # if user not in self.user_conversations:
        #     self.user_conversations[user] = []
            
        self.message_history.append("USER: " + message.author.name + ", USERNAME: " + message.author.global_name + ", CONTENT: " + message.content)
        self.message_history_size += len(self.message_history[-1])
        #self.user_conversations[user].append(len(self.message_history) - 1)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            # {"role": "user", "content": message.content},
        ]
        
        # messages.extend([{"role" : "system" if i % 2 == 1 else "user", "content" : self.message_history[x]} for i, x in enumerate(self.user_conversations[user])])
        messages.extend([{"role": "user" if msg.startswith("USER:") else "system", "content" : msg}  for msg in self.message_history])
        
        print(messages)

        response = await self.client.chat.complete_async(
            model=MISTRAL_MODEL,
            messages=messages,
        )

        chosen_response = response.choices[0].message.content
        self.message_history.append(chosen_response)
        self.message_history_size += len(self.message_history[-1])
        
        while self.message_history_size + len(SYSTEM_PROMPT) > self.size_cap:
            msg_to_delete = self.message_history.pop(0)
            self.message_history_size -= len(msg_to_delete)
        #self.user_conversations[user].append(len(self.message_history) - 1)
        
        return chosen_response
