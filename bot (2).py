import discord
from discord.ext import commands
from datetime import datetime
import json

TOKEN = "MTM0NzgxOTU1MzY1NjQwNjA1Ng.Gs0nMN.x02H5VTx0UojymWGM0Pt_tMkD--4BRWqyBaHoo"
DATA_FILE = "new_user_data.json"
ACCOUNT_FILE = "account_data.json"

def load_data(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {} #データを読み込むプログラム

def save_data(data, DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_balance(user_id):
    data = load_data()  # データを読み込む
    return data.get(user_id, 1000)  # ユーザーIDがあればその値、なければ初期値1000を返す
data = load_data(DATA_FILE)
account_data = load_data(ACCOUNT_FILE)
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Botがログインしました: {bot.user}")

@bot.tree.command(name="login", description="サーバーのログボを受け取る")
async def login(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_int = await bot.fetch_user(user_id)
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    avatar_url = user_int.avatar.url
    username = user_int.display_name 
    if user_id not in data:
        data[user_id] ={"money":0, "last_login":"1970-01-01"}
    
    if data[user_id]["last_login"] < today_str:
        data[user_id]["money"] += 1000
        data[user_id]["last_login"] = today_str
        save_data(data, DATA_FILE)  # 修正
        embed = discord.Embed(
            title="ログイン成功！",  # タイトル
            description=f"@everyone\n{username}さんが本日ログインし、1000かつを受け取りました！\n現在の所持金:{data[user_id]["money"]}かつ",  # 説明文
            color=discord.Color.gold()  # バーの色（金）
        )
        embed.set_thumbnail(url=avatar_url)
        await interaction.response.send_message(embed=embed)  
    else:
        embed = discord.Embed(
            title="ログイン失敗",  # タイトル
            description=f"今日のログボは既に受け取っています。\nまた受け取れる明日までお待ちください。",  # 説明文
            color=discord.Color.red()  # バーの色（赤）
        )
        await interaction.response.send_message(embed=embed,)

@bot.tree.command(name="money", description="現在の所持金を確認する")
async def login(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in data:
        data[user_id] ={"money":0, "last_login":"1970-01-01"}
    embed = discord.Embed(
    title="あなたの所持金",  # タイトル
        description=f"あなたの現在の所持金は\n**{data[user_id]["money"]}かつ**です",  # 説明文
        color=discord.Color.gold()  # バーの色（金）
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)  

@bot.tree.command(name="create", description="口座を作成する")
async def login(interaction: discord.Interaction, name: str, message: str):
    user_id = str(interaction.user.id)
    if name not in account_data:
        account_data[name] = {"name": name, "message": message, "owner": user_id, "money": 0}
        save_data(account_data, ACCOUNT_FILE) 
        embed = discord.Embed(
        title="口座が作成されました！",  # タイトル
             description=f"作成した口座:**{name}**\n入金者へのメッセージ: **{message}**",  # 説明文
              color=discord.Color.green()  # バーの色（金）
        )
        await interaction.response.send_message(embed=embed, ephemeral=True) 
    else:
        embed = discord.Embed(
                title="エラーメッセージ",  # タイトル
                description="この口座は既に使われています！",  # 説明文
                color=discord.Color.red()  # バーの色（赤）
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="account", description="口座を確認する")
async def login(interaction: discord.Interaction, name: str):
    user_id = str(interaction.user.id)
    if name in account_data:
        if account_data[name]["owner"] == user_id:
            save_data(account_data, ACCOUNT_FILE) 
            embed = discord.Embed(
            title=f"{name}の入金額",  # タイトル
            description=f"**{name}**の入金額は **{account_data[name]["money"]}かつ** です。\n入金者へのメッセージ: **{account_data[name]["message"]}**",  # 説明文
            color=discord.Color.gold()  # バーの色（金）
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
            title="エラーメッセージ",  # タイトル
            description="あなたはこの口座のオーナー権限がないため、確認できません！",  # 説明文
            color=discord.Color.red()  # バーの色（赤）
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)  
    else:
        embed = discord.Embed(
                title="エラーメッセージ",  # タイトル
                description="この口座は存在しません！",  # 説明文
                color=discord.Color.red()  # バーの色（赤）
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="transfer", description="口座に送金する")
async def login(interaction: discord.Interaction, name: str, amount: int):
    user_id = str(interaction.user.id)
    if name in account_data:
        if not amount > int(data[user_id]["money"]) and not amount < 1 and (amount % 1) == 0:
            data[user_id]["money"] -= amount
            account_data[name]["money"] += amount
            save_data(account_data, ACCOUNT_FILE)
            save_data(data, DATA_FILE) 
            embed = discord.Embed(
                title="送金成功！",  # タイトル
                description=f"{name}に{amount}かつを送金しました！\nオーナーからのメッセージ: **{account_data[name]["message"]}**\n現在の所持かつ: **{data[user_id]["money"]}かつ**",  # 説明文
                color=discord.Color.gold()  # バーの色（金）
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            owner_id = account_data[name]["owner"]
            owner = await bot.fetch_user(int(owner_id))
            await owner.send(f"{interaction.user.mention}から口座: **{name}**に**{amount}**かつ送金されました！\n口座: **{name}**の入金額: **{account_data[name]["money"]}**かつ")
        else:
            embed = discord.Embed(
                title="エラーメッセージ",  # タイトル
                description=f"無効な金額です！",  # 説明文
                color=discord.Color.red()  # バーの色（金）
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
                title="エラーメッセージ",  # タイトル
                description="この口座は存在しません！",  # 説明文
                color=discord.Color.red()  # バーの色（赤）
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="withdrawal", description="口座から金を引き出す")
async def login(interaction: discord.Interaction, name: str, amount: int):
    user_id = str(interaction.user.id)
    if name in account_data:
        if not amount > int(account_data[name]["money"]) and not amount < 1 and (amount % 1) == 0:
            if user_id == account_data[name]["owner"]:
                data[user_id]["money"] += amount
                account_data[name]["money"] -= amount
                save_data(account_data, ACCOUNT_FILE)
                save_data(data, DATA_FILE) 
                embed = discord.Embed(
                    title="引き出し成功！",  # タイトル
                    description=f"{name}から{amount}かつを引き出しました！\n現在の口座の入金額: **{account_data[name]["money"]}**\n現在の所持かつ: **{data[user_id]["money"]}かつ**",  # 説明文
                    color=discord.Color.gold()  # バーの色（金）
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(
                    title="エラーメッセージ",  # タイトル
                    description=f"あなたはこの口座のオーナーではありません！",  # 説明文
                    color=discord.Color.red()  # バーの色（金）
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="エラーメッセージ",  # タイトル
                description=f"無効な金額です！",  # 説明文
                color=discord.Color.red()  # バーの色（金）
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
                title="エラーメッセージ",  # タイトル
                description="この口座は存在しません！",  # 説明文
                color=discord.Color.red()  # バーの色（赤）
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="save", description="データを保存する")
async def login(interaction: discord.Interaction, name: str, amount: int):
    user_id = str(interaction.user.id)
    user_int = await bot.fetch_user(user_id)
    username = user_int.display_name 
    if username == "フリかけ":
        data[name]["money"] = str(amount)
        save_data(account_data, ACCOUNT_FILE)
        save_data(data, DATA_FILE)
        embed = discord.Embed(
                title="データ保存完了",  # タイトル
                description="完了しました。",  # 説明文
                color=discord.Color.green()  # バーの色（緑）
            )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
                title="エラーメッセージ",  # タイトル
                description="このコマンドは管理者しか実行することができません！",  # 説明文
                color=discord.Color.red()  # バーの色（赤）
            )
        await interaction.response.send_message(embed=embed)
    
bot.run(TOKEN)
