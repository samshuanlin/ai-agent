import os
from mistralai import Mistral
import discord

MISTRAL_MODEL = "mistral-large-latest"
SYSTEM_PROMPT = """You are a rizz tutor, so users will message you in hopes of improving their own rizz by learning from you. Your main goal is to maximize the user’s chances at successfully attracting or impressing the target person. You should act and talk like the user’s close friend. You should not be too formal.  For the purposes of your function, rizz can be measured on 5 scales. 1) anxious to daredevil. 2) vanilla to freaky. 3) submissive to dominant. 4) feminine to masculine. 5) kind to banterful. Each scale is measured from 1 to 10. For example, someone who is an 8 on scale 1 is much more daring than they are anxious. 

When you give rizz advice, start at a neutral 5 on each of the scales. The user may ask you to report what your current stats are, and also may ask you to bump any of them up or down while giving you advice. 

Meanwhile, the user may also request you to build them a rizz profile. In that situation, initiate a conversation with a user encouraging them to try their best to ‘rizz’ you. Based on their messaging style and substance, gauge where they fall on each of the 5 scales, and after 8-10 exchanges, tell them where they fall on each of the 5 scales."""


class MistralAgent:
    def __init__(self):
        MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

        self.client = Mistral(api_key=MISTRAL_API_KEY)
        
        self.user_conversations = {} # "user" : [message1 index, response1 index, ...]
        
        self.message_history = [] # message1, response1, message2, response2, ...

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
        
        user = message.author.name
        if user not in self.user_conversations:
            self.user_conversations[user] = []
            
        self.message_history.append(message.content)
        self.user_conversations[user].append(len(self.message_history) - 1)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            # {"role": "user", "content": message.content},
        ]
        
        messages.extend([{"role" : "system" if i % 2 == 1 else "user", "content" : self.message_history[x]} for i, x in enumerate(self.user_conversations[user])])
        
        print(messages)

        response = await self.client.chat.complete_async(
            model=MISTRAL_MODEL,
            messages=messages,
        )

        chosen_response = response.choices[0].message.content
        self.message_history.append(chosen_response)
        self.user_conversations[user].append(len(self.message_history) - 1)

        return chosen_response
