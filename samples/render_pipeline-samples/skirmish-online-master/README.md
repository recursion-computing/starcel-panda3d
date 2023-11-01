# Skirmish Online

Skrimish Online is a base for a multiplayer, online game ([MMORPG](https://en.wikipedia.org/wiki/Massively_multiplayer_online_role-playing_game) style), written in [Python](https://www.python.org/) with [Panda3D](https://www.panda3d.org/). It uses client-server model, with server and it's memory ([Redis](https://redis.io/)) being ran in a [Docker](https://www.docker.com/) container.

The 3D models used in this game were extracted from [Lineage II Classic](https://www.lineage2.com/en-us/classic) using [UE Viewer](https://www.gildor.org/en/projects/umodel). This game is not intended for any profit.

Thank you [@Doman](https://github.com/ickyicky) for helping with the server, the protocol and for introducing Docker to the project =D.

## Game description

Currently, player can do few things after connecting to the game server:
- run around on the map (WASD),
- chat with other players (press ENTER to type a message),
- use different abilities that deal damage to other players (Q, E, R, F),
- change their character's model (text command "/setmodel <model_id>"),
- change their character's weapon model (text command "/setweapon <weapon_id>"),
- change their nickname (text command "/setname <name>").
- request a sound to be played on every other client (text command "/sound <funny_sound_file_name>", the sound needs to be located on every client in `client/local/assets/sounds`).

Every player has:
- health points that are subtracted when somebody attacks the player; they're restored over time
- mana points that are consumed when the player uses an ability; they're restored over time

After player's death:
- the killed player is teleported to the center of the map,
- the killed player's health and mana points are restored to full,
- the player who dealt the killing blow has his power increased and from now on will deal slightly more damage, the size of his character slightly increases,
- the killed player automatically announces his death in the chat and the player who killed him announces his kill count.

The server detects timeouts and removes players who left the game.

<ins>**In all of these aspects, server and all connected clients are being constantly synchronized.**</ins>

## Screenshots and videos

Here are some screenshots and videos showing state of the project as of 21.07.2022.

<img src="https://raw.githubusercontent.com/marekbobrowski/skirmish-online/master/doc/screenshots/1.png">
<img src="https://raw.githubusercontent.com/marekbobrowski/skirmish-online/master/doc/screenshots/2.png">


https://user-images.githubusercontent.com/49000055/180601512-38ccca6c-144e-4d86-89eb-00e57c4dae08.mp4

https://user-images.githubusercontent.com/49000055/180602562-98c32ae0-a53d-4cba-9f64-7c231b918673.mp4

There's also a longer video on YouTube: [link](https://youtu.be/4J1rMSQ3HlI) (made in old-school style on purpose =D).


## Setting up the project

### Client usage only

Make sure you have [Python](https://www.python.org/) installed. Open the project directory.

1. `pip install -r client-requirements.txt` to install all client dependencies,
2. `python -m client <server IP without brackets>` to run the client.

### Client and server usage

Make sure you have [Python](https://www.python.org/) and [Docker](https://www.docker.com/) installed.
Open the project directory.

1. `pip install -r requirements.txt` to install all dependencies,
2. `docker compose build server` to build the docker image,
3. `docker compose up` to run the server and memory app (redis),
4. `python -m client <server IP without brackets, default is localhost>` to run the client.

## Client Development Manual

This section contains instructions on developing some of the most important parts of the client.

### Adding new GUI elements

The GUI package is located in `client/local/section/main/ui`. That's the place where you can create new class/package for some new GUI element. The file with main class `MainSectionUi` that stores all the GUI elements is called `ui.py`. Following the existing examples attach instance of your new class. If you want your GUI element to be in a fixed position on the screen (i. e. not connected with the 3D world) you will most probably want to pass `self.node` as an argument to your new class (this requires understanding of how [scene graph in Panda3D](https://docs.panda3d.org/1.10/python/programming/scene-graph/index) works). If you want your GUI elements to be connected to the 3D world (most propably player units), you want to pass self.model and then take care of reparenting GUI elements to the units (see `floating_bars.py` as a guide).

Most of the time, UI will update based on the events that were firstly received from the server and then "interpreted" by the client. In `client/event.py` there is a list of those events. In order to make your class respond to chosen events, you need to inherit from `direct.showbase.DirectObject.DirectObject` (Panda3D class) and import all events from `client.event.Event`. Then simply in init method write `self.accept(Event.<some event>, self.event_handler_method)` and in the specified method handle the event by updating your GUI element (you can check verious examples of that in all of the existing GUI classes). In order to know what event arguments are passed with the event, you need to check the place they are called. But for example, with event `UNIT_NAME_UPDATED`, there are passed 2 arguments: unit instance and the unit's old name.

### Create new type of message that can be sent between clients and server

In `protocol/domain` package create a new schema class (it defines components of message - for example, for message that tells about new position of the player, define x, y, z as 64 bit floats). Then in `protocol/messages` create a new message class and assign it the schema that you defined before. Also assing your message a unique ID and message type (for messages sent from client to server it's usually a `MessageType.request`). Remember to import the created message class in package's `__init__.py` so it will be automatically registered in the message bank.  

### Sending new type of message from client to server

In order to send some new kind of information to the server, you need to create a new class inside `client/net/message_sender/senders` package and inherit from `BaseSender`. Specify the managed Event in the `MANAGED_EVENT` class field and the Message type thats's going to be sent in `MESSAGE_CLS` class field (look at the existing examples in the `senders` package). Then "somewhere in the client" call specified event with proper arguments and data should be sent to the server. Remember to import the created sender class in package's `__init__.py` so it will be automatically registered in the sender bank.

### Handling new type of message sent by the server

In order to handle some new kind of information from the server, you need to create a new class inside `client/net/message_handler/handler` package and inherit from `MessageHandler`. Specify the handler message type in the `handled_message` class field so it automitcally reacts to that kind of message. Override the abstract `handle_message` method in which you have to simply handle the message. Usually you will want to instantly fire an event with `core.instance.messenger.send(<event class>, sentArgs=[some, event, arguments])`, so that classes from `client/local` can take care of it. Remember to import the created handler class in package's `__init__.py` so it will be automatically registered in the handlers bank.

The mentioned event is triggered so that some more "substantial" update in the client can happen. Most probably model class of the main section (`client/local/section/main/model/model.MainSectionModel`) will listen for the updates so the game state (model) can be updated. Make that model listen for the mentioned event (`self.accept(<event_class>, <callable_handler>)`). Then in the model's handler you want to update the state of the game (most probably it will be updating some fields of a unit). From there you might want to call another event by using `core.instance.messenger.send(<event class>, sentArgs=[some, event, arguments])`. It's because, for example, you received from the server information about player changing their weapon. In the model class you updated that information. But now you need to actually make it visible in the game scene. So you trigger next event and then proper class (in this case `client/local/section/main/scene/actor_manipulation/manipulator.ActorManipulator`) will take care of changing the weapon visually.

## Server Development Manual

### Sending new type of message from server to client

In order to send some new kind of information to the client, you need to create a new class inside `server/client_notifier/sub_notifiers` package and inherit from `SubNotifierBase`. Specify:
- the Event that will trigger the message to be sent (`MANAGED_EVENT` class field)
- Message class thats's going to be sent (`MESSAGE_CLS` class field)

Look at the existing examples in the mentioned package. Then "somewhere in the server" call specified event with proper arguments and data should be sent to the client. Remember to attach an instance of the created sub_notifier class in `server/client_notifier/notifier.py`.

### Handling new type of message sent by the client

In order to handle some new kind of information from the client, you need to create a new class inside `server/request_handler/message_handlers` package and inherit from `MessageHandler`. Specify the handler message type in the `handled_message` class field so it automitcally reacts to that kind of message. Override the abstract `handle_message` method in which you have to simply handle the message. Remember to import the created handler class in package's `__init__.py` so it will be automatically registered in the handlers bank.

### Working with events

The server application has a very simple event system which you can use in your class by inheriting from the `server/event/event_user.EventUser`. Also import `Event` class from file `server/event/event.py`. To make your class listen to specific event, write `self.accept_event(event=Event.<example>, handler=<callable object>)`. If you want to fire an event, write `self.send_event(event=Event.<example>, prepared_data=<some_data>)`.

### Dealing with memory / game state

In `server/storage/cache` you have classes that deal with updating/accessing the game state. Most of the game memory is stored in a separate docker container with Redis. That's why, for example, in class `server/storage/cache/players.PlayerCache` there are methods like `load()` or `save()` for accessing/modifying the player's data in Redis. Usually, if you want to do any change in the game state, you will firstly load the data from redis and after applying changes you want to save it in redis.

### Adding tasks

There's an option to add tasks per every session/connection/player (whatever you want to call it). Task is an operation that is regularly completed with specified time interval (for example - health or mana regen like in World of Warcraft). To create such task, add new task performer class in `server/tasking/task_performers` and inherit from `TaskPerformerBase`. Specify time interval in seconds by assigning it to `INTERVAL` class field. Override `task_tick()` method to perform some operation on available `Session` object. 

### Adding / handling new spells

In order to create new spell, navigate to `server/spell_handler/handlers` package. Create new class that will inherit from `BaseSpellHandler` and import it in package's `__init__.py` so it's automatically registered in the spell handlers' bank. Currently the spells are quite limited and primitive. They all instantly deal damage and are AoE (since there's no targeting). The only difference is the range of dealt damage, mana cost, cooldown, played animation. You specify those in the class fields `ANIMATION`, `DAMAGE_RANGE`, `MANA_COST` etc. Only with the cooldowns you have to deal inside `server/cache/spells.py` (at least currently).

### Adding / handling new text commands

To create a new text command that can be sent by the client, navigate to `server/text_command_handler/handlers`. Create a class that will inherit from `BaseTextCommandHandler` and import it in package's `__init__.py`. In your new class specify the `KEYWORD` class field (e. g. "/teleport"). Assign `LENGTH` field (an integer) that tells how many arguments your new command requires. Override the abstract method `handle_command()` to handle the command. First passed argument is stored in `self.command_vector[1]`, second is stored in `self.command_vector[2]` etc.
