from discord.ext import commands
import discord
import uuid
import json
from flask import Flask, request, jsonify
import threading
import os

bot = commands.Bot(command_prefix="/", intents=discord.Intents.default())
KEYS_FILE = "keys.json"
app = Flask(__name__)
keys = {}

def save_keys():
    with open(KEYS_FILE, "w") as f:
        json.dump(keys, f)

def load_keys():
    global keys
    try:
        with open(KEYS_FILE, "r") as f:
            keys = json.load(f)
    except:
        keys = {}

@app.route("/verify")
def verify():
    key = request.args.get("key")
    if key in keys and keys[key]["uses"] > 0:
        keys[key]["uses"] -= 1
        if keys[key]["uses"] <= 0:
            del keys[key]
        save_keys()
        return jsonify({ "valid": True })
    return jsonify({ "valid": False })

@bot.command()
async def genkey(ctx, uses: int = 1):
    if ctx.author.guild_permissions.administrator:
        new_key = str(uuid.uuid4()).upper()
        keys[new_key] = { "uses": uses }
        save_keys()
        await ctx.send(f"✅ Generated key: `{new_key}` (uses: {uses})")

@bot.command()
async def delkey(ctx, key: str):
    if ctx.author.guild_permissions.administrator:
        if key in keys:
            del keys[key]
            save_keys()
            await ctx.send(f"🗑️ Deleted key `{key}`")
        else:
            await ctx.send("❌ Key not found")

@bot.command()
async def listkeys(ctx):
    if ctx.author.guild_permissions.administrator:
        if not keys:
            await ctx.send("📭 No active keys.")
        else:
            msg = "\n".join([f"`{k}` → uses: {v['uses']}" for k, v in keys.items()])
            await ctx.send(f"📜 Active Keys:\n{msg}")

def run_api():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    load_keys()
    threading.Thread(target=run_api).start()
    bot.run(os.environ["DISCORD_TOKEN"])
