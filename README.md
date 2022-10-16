# Conversation Chatbot

This project implements a chatbot that carry on a conversation with a user.
One can give the bot a background persona and it will assume the role and chat accordingly.

## API

### Definition

A complete definition of the API is in the Swagger file "swagger.yaml".

### A Usage Example

The base path of the API depends on how the server is deployed.
In this example, the base path `http://localhost:8080/tankabot` is used.

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

## Chatbot Server Deployment

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

####Requirements

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

#### Steps
*TBD by DevOp*





