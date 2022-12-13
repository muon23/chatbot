# Open Domain Chat Bot

This project implements a chatbot that carry on a conversation with a user.
One can give the bot a background persona and it will assume the role and chat accordingly.

## Summarizer API

A complete definition of the API is in the Swagger file "[swagger.yaml](https://gitlab.com/npc-work/npc-work-research/chatbot/-/blob/main/swagger.yaml)".

### A Usage Example

The base path of the API depends on how the server is deployed.
In the following examples, the base path `http://localhost:8080/tankabot` is used.

#### Summarize a Text

The simplest way to summarize a text is with only the "text" field in the request.

```
POST http://localhost:8080/tankabot/summary

{
  "text": "Tianqiao Chen\n@Vincent 朱赟  volunteer 那个功能本身可以是调性的一个重要部分\n21:15\nTianqiao Chen\n调性并不是写写画画，有的时候可以从宣传小的贴心的功能开始\n21:16\nTianqiao Chen\n比方说我们的自动翻译，强调了人和人之间交流不应该有隔阂\n21:16\nTianqiao Chen\n比方说volunteer： 善良有爱心有责任心\n21:17\nTianqiao Chen\n@Evangeline Wang 如果你要好一些功能的调性，不要上来就说这个不对要改正那个\n21:17\nTianqiao Chen\n而是实实在在的增加一些小东西\n21:18\nTianqiao Chen\n而不要急着去改变一个东西。只要改变都会涉及到历史问题\n21:19\nTianqiao Chen\n@Jonathan 比方说我的那个👍，能不能就比所有竞品大，不但体现出潮，而且体现出简单深刻里面的简单这个特点！\n21:19\nTianqiao Chen\n千言万语，一个赞就够了，这个赞岂不是位置要更大一些？\n21:20\nTianqiao Chen\n@Evangeline Wang 这就是软装，这就是调性，多去找一些这些细节不断提升，拿出一个简易表出来\n22:25\nJonathan\nTianqiao Chen\n@Jonathan 比方说我的那个👍，能不能就比所有竞品大，不但体现出潮，而且体现出简单深刻里面的简单这个特点！\n\n陈总这么一说，我有了创意，后面做成demo动效给陈总和大家看。\n22:49\nTianqiao Chen\n呵呵，以后不要等我“这么一说“\n22:50\nJonathan\n哦😄\n23:34\nEvangeline Wang\nTianqiao Chen\n@Evangeline Wang 这就是软装，这就是调性，多去找一些这些细节不断提升，拿出一个简易表出来\n\n明白，我明白陈总的意思了。我把值得优化的点逐个整理出来\n12/1/2022 7:43\nTianqiao Chen\n总结一下你想在tanka 用户里放的label，比方说乐于助人，有责任心\n7:44\nTianqiao Chen\n然后去找地方体现出来\n16:35\nEvangeline Wang\n明白"
}
```

This will get the following response:

```
{
  "version": "0.4.1",
  "summary": "Tianqiao Chen discussed the importance of tone when it comes to developing features for a product. He suggested that instead of immediately changing something, small additions can be made to emphasize the connection between people. For example, he mentioned the automatic translation feature which emphasizes that there should be no barriers between people. He also suggested that volunteer features should emphasize kindness, love, and responsibility. \n\nHe then gave an example of how to improve the tone of a feature. He suggested making the \"like\" button bigger than the competition to emphasize its simplicity and coolness. \n\nFinally, he suggested summarizing the labels that should be used in Tanka for users, such as being helpful and responsible. He then suggested finding ways to emphasize these labels."
}
```

### Specify a Language

One may want to summarize in Chinese (or other languages).  To do this, one may add the "language" field.

```
POST http://localhost:8080/tankabot/summary

{
  "language": "zh",
  "text": "Tianqiao Chen\n@Vincent 朱赟  volunteer 那个功能本身可以是调性的一个重要部分\n21:15\nTianqiao Chen\n调性并不是写写画画，有的时候可以从宣传小的贴心的功能开始\n21:16\nTianqiao Chen\n比方说我们的自动翻译，强调了人和人之间交流不应该有隔阂\n21:16\nTianqiao Chen\n比方说volunteer： 善良有爱心有责任心\n21:17\nTianqiao Chen\n@Evangeline Wang 如果你要好一些功能的调性，不要上来就说这个不对要改正那个\n21:17\nTianqiao Chen\n而是实实在在的增加一些小东西\n21:18\nTianqiao Chen\n而不要急着去改变一个东西。只要改变都会涉及到历史问题\n21:19\nTianqiao Chen\n@Jonathan 比方说我的那个👍，能不能就比所有竞品大，不但体现出潮，而且体现出简单深刻里面的简单这个特点！\n21:19\nTianqiao Chen\n千言万语，一个赞就够了，这个赞岂不是位置要更大一些？\n21:20\nTianqiao Chen\n@Evangeline Wang 这就是软装，这就是调性，多去找一些这些细节不断提升，拿出一个简易表出来\n22:25\nJonathan\nTianqiao Chen\n@Jonathan 比方说我的那个👍，能不能就比所有竞品大，不但体现出潮，而且体现出简单深刻里面的简单这个特点！\n\n陈总这么一说，我有了创意，后面做成demo动效给陈总和大家看。\n22:49\nTianqiao Chen\n呵呵，以后不要等我“这么一说“\n22:50\nJonathan\n哦😄\n23:34\nEvangeline Wang\nTianqiao Chen\n@Evangeline Wang 这就是软装，这就是调性，多去找一些这些细节不断提升，拿出一个简易表出来\n\n明白，我明白陈总的意思了。我把值得优化的点逐个整理出来\n12/1/2022 7:43\nTianqiao Chen\n总结一下你想在tanka 用户里放的label，比方说乐于助人，有责任心\n7:44\nTianqiao Chen\n然后去找地方体现出来\n16:35\nEvangeline Wang\n明白"
}
```

This may get the result like this:

```
{
  "version": "0.4.1",
  "summary": "陈天桥在讨论如何调性的时候，提出了一些有用的建议。他建议不要急着去改变一个东西，而是实实在在的增加一些小东西，比如自动翻译，强调人与人之间的交流不应该有隔阂。此外，他还提到了volunteer，善良有爱心有责任心，这也是一种调性。\n\n他还提到了一个具体的例子，就是👍，能不能就比所有竞品大，不但体现出潮，而且体现出简单深刻里面的简单这个特点！最后，他总结了一下想要在tanka用户里放的label，比如乐于助人，有责任心等等。",
  "language": "zh"
}
```

### Recommend some Titles

One may want the bot to recommend some titles.
This can be done with the "mode" field set to "title".
An optional field "numTitles" can be set for number of titles generated.  The default is 3.

```
POST http://localhost:8080/tankabot/summary

{
  "mode": "title",
  "numTitles": 4,
  "language": "zh",
  "text": "Tianqiao Chen\n@Vincent 朱赟  volunteer 那个功能本身可以是调性的一个重要部分\n21:15\nTianqiao Chen\n调性并不是写写画画，有的时候可以从宣传小的贴心的功能开始\n21:16\nTianqiao Chen\n比方说我们的自动翻译，强调了人和人之间交流不应该有隔阂\n21:16\nTianqiao Chen\n比方说volunteer： 善良有爱心有责任心\n21:17\nTianqiao Chen\n@Evangeline Wang 如果你要好一些功能的调性，不要上来就说这个不对要改正那个\n21:17\nTianqiao Chen\n而是实实在在的增加一些小东西\n21:18\nTianqiao Chen\n而不要急着去改变一个东西。只要改变都会涉及到历史问题\n21:19\nTianqiao Chen\n@Jonathan 比方说我的那个👍，能不能就比所有竞品大，不但体现出潮，而且体现出简单深刻里面的简单这个特点！\n21:19\nTianqiao Chen\n千言万语，一个赞就够了，这个赞岂不是位置要更大一些？\n21:20\nTianqiao Chen\n@Evangeline Wang 这就是软装，这就是调性，多去找一些这些细节不断提升，拿出一个简易表出来\n22:25\nJonathan\nTianqiao Chen\n@Jonathan 比方说我的那个👍，能不能就比所有竞品大，不但体现出潮，而且体现出简单深刻里面的简单这个特点！\n\n陈总这么一说，我有了创意，后面做成demo动效给陈总和大家看。\n22:49\nTianqiao Chen\n呵呵，以后不要等我“这么一说“\n22:50\nJonathan\n哦😄\n23:34\nEvangeline Wang\nTianqiao Chen\n@Evangeline Wang 这就是软装，这就是调性，多去找一些这些细节不断提升，拿出一个简易表出来\n\n明白，我明白陈总的意思了。我把值得优化的点逐个整理出来\n12/1/2022 7:43\nTianqiao Chen\n总结一下你想在tanka 用户里放的label，比方说乐于助人，有责任心\n7:44\nTianqiao Chen\n然后去找地方体现出来\n16:35\nEvangeline Wang\n明白"
}
```

This results in:

```
{
  "version": "0.4.1",
  "title": "1. 调性：从小功能开始\n2. 如何改善用户体验：软装的重要性\n3. 乐于助人，有责任心：Tanka用户的标签\n4. 简单深刻：如何改变一个功能",
  "language": "zh"
}
```

### Create a Reminder
```
POST http://localhost:8080/tankabot/summary

{
  "language": "en",
  "mode": "reminder",
  "text": "gong: 华哥，关于获取数据的事情，和相关人沟通了下时间，定于今天下午5点左右讨论下，不知道这个时间点对你这边是否合适？ Hua Zhang: 我有空的 gong: 好的 华哥，花花现在还在面试，大概还需要10分钟左右，5点我们是先讨论还是等花花结束后一起 Hua Zhang: 等一下他吧 gong: 好的",
  "prompt": ""
}
```

A possible result:

```
{
  "version": "0.4.1",
  "reminder": "Reminder: Discuss data acquisition at 5 pm today.",
  "language": "en"
}
```

### Runtime Errors

The following errors needs to propagated to the client side (frontend).

- **GPT-3 access failed after {tries} tries.  Please try later.**: Something wrong with the GPT-3 service or the connection to GPT-3.
Service is not available at the moment.
- **Content exceeds max number of words.  Please split into shorter contents.**: This indicates that the user supplies a content that is too long.
We shall recommend the user to split the content into smaller pieces.

## Chat Bot API

### Definition

A complete definition of the API is in the Swagger file "[swagger.yaml](https://gitlab.com/npc-work/npc-work-research/chatbot/-/blob/main/swagger.yaml)".

### A Usage Example

The base path of the API depends on how the server is deployed.
In the following examples, the base path `http://localhost:8080/tankabot` is used.

#### Create a Persona for the bot

The first step is to create a bot with its persona.
This is achieves by a POST method to the `persona` API, with the request body similar to the following.

```
POST http://localhost:8080/tankabot/persona

{
  "persona": [
    "I live in New York City", 
    "I like cheese", 
    "I like to swim",
    "I am a woman", 
    "I am an accountant",
  ],
  "name": "Alice",
  "model": "bb2-1B"
}
```

Here, the `persona` field contains a list of sentences describing who the bot is.
They shall be stated as the bot's self-introduction.
That is, use "I" in the sentence.
This field is optional.  If it is not given, the bot takes on no particular persona.

(*Note: BB2 models doesn't handle "My" sentences too well, so use only "I" for a better experience.*)

The `name` field gives the bot a name.  This is optional.
If it is not given, the bot is named "Bot".

The `model` field specifies what chatbot model to use.
It is optional and the default is "bb2-1B".
Currently, the following models are available:
- bb2-400M: Blenderbot 2, 400M training set, Transformers library.
- bb2-1B: Blenderbot 2, 1B training set, Transformers library.
- bb2-3B: Blenderbot 2, 3B training set, ParlAI library.
- gpt3: GPT-3.  An Open AI key is required.

If successful, the server shall send back this response:

```
{
  "version": "0.1.0",
  "persona": "634a383d6890320d447b9878",
  "name": "Alice",
  "model": "facebook/blenderbot-1B-distill"
}
```

The `version` field shows the server version.

The `persona` field is the "persona ID" for this bot.
This shall be used in the later API to specify which bot the user wishes to talk to.

The `name` and `model` fields are the names of the bot and model used, for information.

#### Chat with the bot

Once the ID of the persona is obtained, one can chat to the bot with a POST method to the `chat` API with the persona ID.

```
POST  http://localhost:8080/tankabot/chat/634a383d6890320d447b9878

{
  "utterance": "Hey, long time no see.  How are you doing?"
}
```

The `utterance` field is what one wants to talk to the bot.

If successful, the server may respond with something similar to this:

```
{
  "version": "0.1.0",
  "persona": "634a383d6890320d447b9878",
  "name": "Alice",
  "reply": " I am doing well.  Just got back from the gym.  What are you up to?"
}
```

The `version`, `persona` and `name` fields are like before.
The `reply` field is what the bot responded to one's utterance in the request.

One can continue to use this API to conduct a conversation with the bot as long as one likes.

#### Review the conversation with the bot

After a few rounds, one may want to review all the previous conversation with the bot.
This is done with a GET method to the `chat` API with the persona ID.

```
GET  http://localhost:8080/tankabot/chat/634a383d6890320d447b9878
```

The server may respond with this:

```
{
  "version": "0.1.0",
  "persona": "634a383d6890320d447b9878",
  "name": "Alice",
  "conversation": [
    "You: Hey, long time no see.  How are you doing?",
    "Alice:  I am doing well.  Just got back from the gym.  What are you up to?",
    "You: Oh, how nice.  What do you do there?",
    "Alice:  I work as a financial analyst.  It is a lot of work, but I enjoy it.",
    "You: No, I mean what did you do in the gym?",
    "Alice:  Oh, sorry!  I meant to say I enjoy swimming.  Do you have any hobbies?",
    "You: Not a sporty person.  I like oil painting.  It releases the stress of work.  I guess swimming does the same thing to you too, doesn't it?",
    "Alice:  Yes, it is very relaxing.  How long have you been an oil painter?",
    "You: My first oil painting was like 20 years ago, but I don't do that everyday.",
    "Alice:  Wow, that is a long time.  What kind of paintings do you like to paint?",
    "You: I am in to protrait painting recently",
    "Alice:  That sounds like a lot of fun.  Have you ever painted landscapes?",
    "You: I started with landscapes, but I found it is less challenging now",
    "Alice:  That makes sense.  Do you have a favorite landscape that you have painted?"
  ]
}
```

The `conversation` field lists one's conversation with the bot so far.

#### Reset the conversation

If one want the bot to forget about the current conversation, one may add a `reset` field to the `chat` POST API request.

```
POST  http://localhost:8080/tankabot/chat/634a383d6890320d447b9878

{
  "utterance": "Hello.",
  "reset": true
}
```

And the server may respond:

```
{
  "version": "0.1.0",
  "persona": "634a383d6890320d447b9878",
  "name": "Alice",
  "reply": " What do you do for a living?  I work in accounting.  Do you have any hobbies?"
}
```

If one use the GET method, he shall see the previous session of the conversation are all gone.

```
GET  http://localhost:8080/tankabot/chat/634a383d6890320d447b9878
```
``` 
{
  "version": "0.1.0",
  "persona": "634a383d6890320d447b9878",
  "name": "Alice",
  "conversation": [
    "You: Hello.",
    "Alice:  What do you do for a living?  I work in accounting.  Do you have any hobbies?"
  ]
}
```

#### Delete the persona

One can delete a persona with a DELETE method to the `persona` API.

```
DELETE   http://localhost:8080/tankabot/persona/634a383d6890320d447b9878
```

If he trys to access the bot with the same ID, he will get this error in response.

```
GET  http://localhost:8080/tankabot/chat/634a383d6890320d447b9878

{
  "error": "persona 634a383d6890320d447b9878 not found"
}
```

If a persona is not accessed for a period, it will be automatically deleted.
The duration is configured by the system.  The default is one day.

## Chat Bot Dialog Editing

**(This currently only works for GPT-3 model.)**

Sometimes, you may not like some utterances in the dialog.
The API in this section allows you to delete or replace them.

The example in the section is generated by this persona:

```
POST  http://localhost:8082/tankabot/persona

{
  "persona": [
    "I came a long way to this swampy planet, seeking your wisdom.",
    "I asked you to train me as a Jedi warrior.",
    "You are teaching me how to use the Force."
    ],
  "name": "Luke",
  "model": "gpt3"
}
```

### Enumerate the Utterances

To be able to indicate which of utterances to edit, you need to enumerate them.
This is achieved by an argument `enumerate=1` in the GET request of the chat API.
For example:

```
GET  http://localhost:8082/tankabot/chat/635d7b1022a554bb67297cb5?enumerate=1
```

Then, the utterances are numbered for your reference.

```
{
  "version": "0.3.1",
  "persona": "635d7b1022a554bb67297cb5",
  "name": "Luke",
  "model": "GPT-3 Davinci",
  "conversation": [
    "  0. You: you know nothing that i said",
    "  1. Luke: you are not jedi Master Yoda, you are just a little green Muppet.",
    "  2. You: i... i... no! i am not!  be polite to your master, young skywalker.  force is too strong in you.",
    "  3. Luke: i am not a jedi and i will never be.  i will kill my father and join the dark side! (Luke hits me on the head wiht his light saber)",
    "  4. You: ouch!  what do you do that for.  dark side, you will go not.  ...uh, was that the correct yoda grammar that I just said?",
    "  5. Luke: ...maybe, i just don't like you.",
    "  6. You: hey, i had an easy life in the swamp, and it is YOU who came to here to dig me out of my retirement.  and you haven't paid your tuition!",
    "  7. Luke: tuition?  i thought this was a free service for jedi training.",
    "  8. You: free?  who told you so?",
    "  9. Luke: ...you did.  see, i looked at the manual of jedi training..",
    " 10. You: Oh.  It said 'first hour is free'.  You have been here for a week now.  Pay up!",
    " 11. Luke: well, we have a problem, then.  i don't got any money.",
    " 12. You: no money?  then your ship is mine!",
    " 13. Luke: no no no, i can't give you my ship.  it's the only thing left that i have in the galaxy.  please, don't take my ship away."
  ]
}
```

### Redo the Last Interaction

If you don't like AI's last response, you can add a "redo" in your request like this:

```
POST  http://localhost:8082/tankabot/chat/635d7b1022a554bb67297cb5

{
   "redo": 1,
   "utterance": "no money?  then your ship is mine!"
}
```

The value of "redo" can be anything other than "false" or "0".
The last pair of utterances become:

```
    ...
    " 11. Luke: well, we have a problem, then.  i don't got any money.",
    " 12. You: no money?  then your ship is mine!",
    " 13. Luke: no, my ship is not yours!  ...i just said that to get you off my back."
    ...
```

### Hide or Un-hide Dialogs from AI

You can hide some utterances, so they won't be used by the AI to generate its next response.

```
{
   "hide": ["-1", 4, "6-8", "11-"],
   "utterance": "off your back?  no, i am going to ride on your back and we'll traveling around the planet!"
}
```
The `hide` property is a list of utterance numbers that you wish to hide.
They can be integers, or a string indicates the range.
The range can be specified by two integers seperated by a `-` or `:`.
If the first number is not specified, 0 is assumed.
If the second number is omitted, the last one in the conversation is assumed.
If there is only one element in the list, you don't need the list bracket.

If you list the conversation again, you can see the `(hidden)` marks in the utterances.
AI generates a new response without looking at those hidden utterances.

```
  "conversation": [
    "  0. You: you know nothing that i said (hidden)",
    "  1. Luke: you are not jedi Master Yoda, you are just a little green Muppet. (hidden)",
    "  2. You: i... i... no! i am not!  be polite to your master, young skywalker.  force is too strong in you.",
    "  3. Luke: i am not a jedi and i will never be.  i will kill my father and join the dark side! (Luke hits me on the head wiht his light saber)",
    "  4. You: ouch!  what do you do that for.  dark side, you will go not.  ...uh, was that the correct yoda grammar that I just said? (hidden)",
    "  5. Luke: ...maybe, i just don't like you.",
    "  6. You: hey, i had an easy life in the swamp, and it is YOU who came to here to dig me out of my retirement.  and you haven't paid your tuition! (hidden)",
    "  7. Luke: tuition?  i thought this was a free service for jedi training. (hidden)",
    "  8. You: free?  who told you so? (hidden)",
    "  9. Luke: ...you did.  see, i looked at the manual of jedi training..",
    " 10. You: Oh.  It said 'first hour is free'.  You have been here for a week now.  Pay up!",
    " 11. Luke: well, we have a problem, then.  i don't got any money. (hidden)",
    " 12. You: no money?  then your ship is mine! (hidden)",
    " 13. Luke: no, my ship is not yours!  ...i just said that to get you off my back. (hidden)",
    " 14. You: off your back?  no, i am going to ride on your back and we'll traveling around the planet!",
    " 15. Luke: ah!  i don't want you to ride on my back!"
  ]
```

You can hide all AI generated text by the `hide_ai` property.

```
{
   "hide_ai": true
}
```

Similar to the `undo`, you can use any values except for 0 or "false".

Also note that if you do not include the `utterance` property, AI will not generate new response.

You can un-hide the hidden utterances with `show`.  For example:

```
{
   "show": "-"
}
```

The `show` property can be specified like the `hide` property.
Here, we put a `"-"` to show everything from 0 to the last.

### Erase Dialogs

If you don't like how the conversation is heading, you can erase some utterances.

```
{
   "erase": "12-",
   "utterance": "no money?  Then, I'll file a credit report on you, so you won't be able to borrow from the bank anymore."
}
```

Here, we erase utterance 12 onward and have AI generate a response on the new input.
The `erase` property can be specified as a list, like the `hide` property above.
The difference is with the `erase`, the utterances are gone for good.

```
...
    " 11. Luke: well, we have a problem, then.  i don't got any money.",
    " 12. You: no money?  Then, I'll file a credit report on you, so you won't be able to borrow from the bank anymore.",
    " 13. Luke: (sarcastic) oh, yoda, you are a jedi master, indeed.  i admire your wisdom and power of the force."
```

### Replace Utterances

You can replace an utterance with a `replace` property:

```
{
    "replace": "10: It said: 'first hour is free', you moron.  You have been here for a week now.  Pay up!"
}
```

This changes the 10th utterance from:

```
    " 10. You: Oh.  It said 'first hour is free'.  You have been here for a week now.  Pay up!",
```

to

```
    " 10. You: It said: 'first hour is free', you moron.  You have been here for a week now.  Pay up!",
```

Multiple utterances may be updated at the same time by putting them in a list, like this:

```
    "replace": [
        "10: It said: 'first hour is free', you moron.  You have been here for a week now.  Pay up!",
        "2: No, I am not!!  Behave yourself.  Force is too strong in you young Skywalker"
        ]
```

### Manually Adding Dialogs

Sometimes, you may want to work on the conversation yourself, instead of using AI.
You can add utterances manually at the end of the dialog like this:

```
{
    "script": [
      "That's it!",
      [1, 
        "your ship is mine.",
        "I am going to sell it to the Jawas to cover your tuition"
        ],
      "no.. yoda!  i have to use that to get out of this galaxy!"
    ]
}
```
The `script` property contains a list of utterances.
Each element in the list may be a string or a list.

Our dialog becomes:

```
    ....
    " 13. Luke: (sarcastic) oh, yoda, you are a jedi master, indeed.  i admire your wisdom and power of the force.",
    " 14. You: Me  That's it!",
    " 15. You: your ship is mine.  I am going to sell it to the Jawas to cover your tuition",
    " 16. Luke: no.. yoda!  i have to use that to get out of this galaxy!"
```

By default, the elements in the list alternates between the speakers.
That is why utterance 14 belongs to the user's.

When an element is a list, the strings inside it are concatenated, so you don't have to type everything in one line.
In addition, if the first element is 1 or "Me" ("我" if the name of the persona is in Chinese),
it overrides the order of the speaker and make the utterance the user's.  That is why utterance 15 is from "You".
Similarly, when the first element is 0 or the name of the persona, it forces the following text to be the character's.

Utterance 16 is a single string, so it is the other speaker after utterance 15.
Therefore, it is from Luke without needing to say so in the script.


## Chat Bot Server Deployment

### Run locally

#### Requirements
Make sure the local environment satisfies the following:

- Python3.8+ is required.   Python3.9 is encouraged because this project is developed and tested with it.
- Other Python package requirements see `deployment/requirements.txt`.
- Open AI key if you want to use "gpt3" model.

#### Steps
1. Clone this project
2. Clone the [commons project](https://gitlab.com/npc-work/npc-work-research/commons) at the same directory as this project.
3. Go to the `deployment` of this project.
4. Go to the `deployment/local` of this project.  Edit the file `environemnt` to customize any environment variable if needed.
5. If you want to use "gpt3" model, define environment variable OPENAI_KEY.
6. Run `python3 chatbot.py local` to start the server

### Run on a local Docker

#### Requirements

- 16G memory reserved for the image

#### Steps
1. Clone this project
2. Clone the [commons project](https://gitlab.com/npc-work/npc-work-research/commons) at the same directory as this project.
3. Go to the `deployment` of this project.
4. Go to the `deployment/local` of this project.  Edit the file `environemnt` to customize any environment variable if needed.
5. Run `docker.sh`.  This will run a fresh docker image and enter it.
6. At the docker prompt, `cd` to go to the `home` directory, where you can see both `chatbot` and `commons` projects.
7. `cd chatbot/deployment`
8. `./setup-pip.sh` to download python3.9, necessary packages, and chatbot models.  This will take a while.
9. If you want to use "gpt3" model, define environment variable OPENAI_KEY.
10. `python3 chatbot.py local` to run the server

### Deploy to AWS

#### Requirement

- Internet connection is needed for GPT-3 model access
- OPENAI_KEY environment variable set in a secure manner
- Periodically issue GET to the `/health` API.
In addition to being heartbeat for the health of the server, this also triggers the purging of inactive bots.

#### Steps
*TBD by DevOp*





