
import os
import discord
from dotenv import load_dotenv
import chess

emojis_names = {
    "R":"rook_ws",
    "N":"horse_ws",
    "B":"bishop_ws",
    "Q":"queen_ws",
    "K":"king_ws",
    "P":"pawn_ws",
    "r":"rook_bs",
    "n":"horse_bs",
    "b":"bishop_bs",
    "q":"queen_bs",
    "k":"king_bs",
    "p":"pawn_bs",
}

colnames = {
    0:":regional_indicator_a:",
    1:":regional_indicator_b:",
    2:":regional_indicator_c:",
    3:":regional_indicator_d:",
    4:":regional_indicator_e:",
    5:":regional_indicator_f:",
    6:":regional_indicator_g:",
    7:":regional_indicator_h:"
}

linenames = {
    0:":eight:",
    1:":seven:",
    2:":six:",
    3:":five:",
    4:":four:",
    5:":three:",
    6:":two:",
    7:":one:",
}

emojis = {}

client = discord.Client()
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
commands_channel_name = os.getenv('CHANNEL')
commands_channel = None

board = chess.Board()

async def init_emojis(guild):
    for k in emojis_names.keys():
        name = emojis_names[k]
        for emoji in guild.emojis:
            if emoji.name == name:
                emojis[k] = str(emoji)
    print("Initialized emojis")

async def show_board(channel):
    raw = str(board)
    raw = raw.replace(" ","")
    emojized = ":brown_square:"
    for i in range(0,8):
        emojized += colnames[i]
    emojized += "\n"
    emojized += linenames[0]
    line = 0
    column = 0
    white = True
    for c in raw:
        if c in emojis:
            emojized += emojis[c]
        elif c == ".":
            if white:
                emojized += ":white_large_square:"
            else:
                emojized += ":black_large_square:"
        else:
            emojized += c
        white = not white
        if c == '\n':
            white = line % 2 == 1
            line += 1
            column = 0
            emojized += linenames[line]
        column += 1
    await channel.send(emojized)

async def new_game(channel):
    global board
    board = chess.Board()
    await channel.send("Board has been reset")
    await show_board(channel)

async def detect_end(channel):
    if board.is_game_over():
        await channel.send("Game over")
        await new_game(channel)

@client.event
async def on_message(message):
    global board
    global commands_channel
    if commands_channel == None:
        for channel in message.guild.channels:
            if channel.name == commands_channel_name:
                commands_channel = channel
                break
    if len(emojis.items()) == 0:
        await init_emojis(message.channel.guild)
    if message.channel != commands_channel:
        return
    if message.author == client.user:
        return
    if message.content == ".new":
        await new_game(message.channel)    
    if message.content == ".moves":
        to_send = "Legal moves are:\n```"
        for move in board.legal_moves:
            to_send += str(move) + ","
        to_send = to_send[:-1]
        to_send += "```"
        await message.channel.send(to_send)
    if message.content == ".undo":
        board.pop()
        await show_board(message.channel)
    if len(message.content.split(" ")) > 0:
        if message.content.split(" ")[0] == ".move":
            bits = message.content.split(" ")
            print(bits)
            if len(bits) == 2:
                move = chess.Move.from_uci(bits[1])
                if move in board.legal_moves:
                    board.push(move)
                    await show_board(message.channel)
                    await detect_end(message.channel)
                else:
                    await message.channel.send("Invalid move.")
    



client.run(token)
