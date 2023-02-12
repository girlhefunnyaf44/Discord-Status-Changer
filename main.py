import asyncio
import threading
import time
import zipfile
import customtkinter as tk
from tkinter import PhotoImage, messagebox
import os
import requests
import discord
import webbrowser
from cryptography.fernet import Fernet


class DiscordClient(discord.Client):
    def __init__(self):
        super().__init__()

    async def start_client(self, token):
        await self.start(token, bot=False)


class Window(tk.CTk):
    def __init__(self):
        super().__init__()
        self.LAVENDAR = "#BB78D8"
        self.CHERUB = "#EFB8ED"
        self.CAROUSEL_PINK = "#F6D8F1"
        self.BILOBA_FLOWER = "#CD98E5"
        self.main_frame = None
        self.background_frames = []
        for file in os.listdir(os.getcwd() + "/assets"):
            if file.startswith("main_screen_frame-") and file.endswith(".png"):
                self.background_frames.append(PhotoImage(file=os.getcwd() + "/assets/" + file))
        self.version = 2.3
        self.is_latest_version = self.check_is_latest_version()
        self.title("Discord Status Clapper")
        self.geometry("850x600")
        self.discord = DiscordClient()
        self.side_menu_active = False
        self.iconbitmap(os.getcwd() + "/assets/icon.ico")

    def check_is_latest_version(self):
        latest = requests.get("https://api.github.com/repos/girlhefunnyaf44/discord-status-changer/releases/latest")
        latest = latest.json()
        if float(latest["tag_name"].strip("v")) > self.version:
            return False
        else:
            return True

    def update_side_menu(self, small_side_menu_frame, side_menu_frame):
        if self.side_menu_active:
            small_side_menu_frame.place(x=0, y=0)
            self.main_frame.tkraise()
            small_side_menu_frame.tkraise()
            self.side_menu_active = False
        else:
            small_side_menu_frame.place(x=200, y=0)
            side_menu_frame.tkraise()
            self.side_menu_active = True

    async def handle_status_change(self, selected, what_to_do, twitch_link=None):
        if selected == "stream":
            await self.discord.change_presence(activity=discord.Streaming(name=what_to_do, url=twitch_link))
        elif selected == "listen to":
            await self.discord.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,
                                                                         name=what_to_do))
        elif selected == "watch":
            await self.discord.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                                         name=what_to_do))
        else:
            await self.discord.change_presence(activity=discord.Game(name=what_to_do))
        self.client_screen()

    def selection_page(self, selection):
        num = 0
        for widget in self.main_frame.winfo_children():
            if num != 0:
                widget.destroy()
            num += 1
        do_what_entry = tk.CTkEntry(self.main_frame, placeholder_text=f"What do you want to \"{selection}\"?",
                                    width=190, height=55, bg_color="#BB95E8", fg_color=self.LAVENDAR,
                                    placeholder_text_color="#000000", text_color="#000000",
                                    border_color=self.CAROUSEL_PINK)
        stream_link_entry = tk.CTkEntry(self.main_frame, placeholder_text=f"Twitch Link (Live not needed)", width=190,
                                        height=55, bg_color="#BB95E8", fg_color=self.LAVENDAR,
                                        placeholder_text_color="#000000", text_color="#000000",
                                        border_color=self.CAROUSEL_PINK)
        submit_button = tk.CTkButton(self.main_frame, text="Submit", text_color="#000000", width=190, height=40,
                                     bg_color="#BB95E8", fg_color=self.LAVENDAR, hover_color=self.CAROUSEL_PINK,
                                     command=lambda: asyncio.run(self.handle_status_change(selection,
                                                                                           do_what_entry.get(),
                                                                                           stream_link_entry.get())))
        if selection != "stream":
            do_what_entry.place(x=330, y=250)
            submit_button.place(x=330, y=310)
        else:
            do_what_entry.place(x=330, y=220)
            stream_link_entry.place(x=330, y=280)
            submit_button.place(x=330, y=340)

    def client_screen(self, login=False):
        num = 0
        for widget in self.main_frame.winfo_children():
            if num != 0:
                widget.destroy()
            num += 1
        if login:
            while self.discord.user is None:
                pass
            messagebox.showinfo("Logged in", f"Logged into discord user: {self.discord.user}")
        stream_button = tk.CTkButton(self.main_frame, text="Stream", width=190, height=40, text_color="#000000",
                                     bg_color="#BB95E8", fg_color=self.LAVENDAR, hover_color=self.CAROUSEL_PINK,
                                     command=lambda: self.selection_page("stream"))
        stream_button.place(x=330, y=175)
        listen_button = tk.CTkButton(self.main_frame, text="Listen", width=190, height=40, text_color="#000000",
                                     bg_color="#BB95E8", fg_color=self.LAVENDAR, hover_color=self.CAROUSEL_PINK,
                                     command=lambda: self.selection_page("listen to"))
        listen_button.place(x=330, y=220)
        watch_button = tk.CTkButton(self.main_frame, text="Watch", width=190, height=40, text_color="#000000",
                                    bg_color="#BB95E8", fg_color=self.LAVENDAR, hover_color=self.CAROUSEL_PINK,
                                    command=lambda: self.selection_page("watch"))
        watch_button.place(x=330, y=265)
        play_button = tk.CTkButton(self.main_frame, text="Play", width=190, height=40, text_color="#000000",
                                   bg_color="#BB95E8", fg_color=self.LAVENDAR, hover_color=self.CAROUSEL_PINK,
                                   command=lambda: self.selection_page("play"))
        play_button.place(x=330, y=310)

    def start_discord_client(self, token_passed, quick_login, save_login):
        key = bytes('5IVT18NUc021Ens150IWbTguLfeWgBZ8yvl8o0791c4=', 'utf8')
        fernet = Fernet(key)
        if quick_login:
            with open(os.getcwd() + "/data/login.txt", "rb") as file:
                token = file.read()
                if token != b"":
                    token = fernet.decrypt(token).decode()
                    discord_thread = threading.Thread(target=lambda: asyncio.run(
                        self.discord.start_client(token.strip("\"").strip())))
                    discord_thread.start()
                    self.client_screen(True)
                else:
                    messagebox.showinfo("Missing Information",
                                        "To use 'Quick Login' please enter your token and use 'Login & Save'")
        elif save_login:
            with open(os.getcwd() + "/data/login.txt", "wb") as file:
                file.write(fernet.encrypt(token_passed.encode()))
            discord_thread = threading.Thread(target=lambda: asyncio.run(
                self.discord.start_client(token_passed.strip("\"").strip())))
            discord_thread.start()
            self.client_screen(True)
        else:
            discord_thread = threading.Thread(target=lambda: asyncio.run(
                self.discord.start_client(token_passed.strip("\"").strip())))
            discord_thread.start()
            self.client_screen(True)

    def handle_update(self):
        cwd = os.getcwd()
        for widget in self.winfo_children():
            widget.destroy()
        latest = requests.get("https://api.github.com/repos/girlhefunnyaf44/discord-status-changer/releases/latest")
        latest = latest.json()
        latest_info = requests.get(latest["assets_url"])
        download_url = None
        name = None
        for asset in latest_info.json():
            if asset["name"].endswith(".zip"):
                name = asset["name"][:-4].replace(".", " ", 3)
                download_url = asset["browser_download_url"]
                break
        response = requests.get(download_url)
        with open(cwd + "/latest.zip", "wb") as file:
            file.write(response.content)
        with zipfile.ZipFile(cwd + "/latest.zip") as file:
            file.extractall(cwd + "/../")
        os.remove(cwd + "/latest.zip")
        info_label = tk.CTkLabel(self,
                                 text=f"Downloaded, path: {os.path.abspath(os.path.join(cwd, os.pardir))}\\{name}",
                                 width=850, height=600)
        info_label.place(x=0, y=0)

    def play_background(self, image_space):
        while True:
            for x in range(len(self.background_frames)):
                try:
                    image_space.configure(image=self.background_frames[x])
                    time.sleep(0.5)
                except Exception:
                    pass

    @staticmethod
    def handle_side_button_hover(button, image):
        button.configure(image=image)

    def main_screen(self):
        # FRAMES, BACKGROUND AND SETTINGS
        self.resizable(width=False, height=False)

        side_menu_frame = tk.CTkFrame(self, width=200, height=600, fg_color=self.CHERUB, bg_color=self.CHERUB)
        side_menu_frame.place(x=0, y=0)

        self.main_frame = tk.CTkFrame(self, height=600, width=850, fg_color="#212325")
        self.main_frame.place(x=0, y=0)

        background = tk.CTkLabel(self.main_frame, width=850, height=600, text="")
        background.place(x=0, y=0)
        background_thread = threading.Thread(target=self.play_background, args=[background])
        background_thread.start()

        # SIDE MENU
        github_button = tk.CTkButton(side_menu_frame, text="Project GitHub", width=190, height=40, text_color="#000000",
                                     fg_color=self.LAVENDAR, hover_color=self.CAROUSEL_PINK,
                                     command=lambda: webbrowser.open(
                                         "https://github.com/girlhefunnyaf44/discord-status-changer"))
        github_button.place(x=5, y=5)
        tyclonie_github = tk.CTkButton(side_menu_frame, text="Tyclonie GitHub", width=190, height=40,
                                       text_color="#000000", fg_color=self.LAVENDAR, hover_color=self.CAROUSEL_PINK,
                                       command=lambda: webbrowser.open("https://github.com/Tyclonie"))
        tyclonie_github.place(x=5, y=50)
        bigcountry_github = tk.CTkButton(side_menu_frame, text="BigCountry Github", width=190, height=40,
                                         text_color="#000000", fg_color=self.LAVENDAR, hover_color=self.CAROUSEL_PINK,
                                         command=lambda: webbrowser.open("https://github.com/girlhefunnyaf44"))
        bigcountry_github.place(x=5, y=95)
        watermark_label = tk.CTkLabel(side_menu_frame, text="Developed By Tyclonie & BigCountry", text_color="#000000",
                                      text_font=("Roboto", 5), width=200)
        watermark_label.place(x=0, y=575)

        # MAIN PAGE

        side_bar_button_image = PhotoImage(file=os.getcwd() + "/assets/button.png")
        side_bar_button_hover_image = PhotoImage(file=os.getcwd() + "/assets/button_hover.png")
        side_menu_button = tk.CTkButton(self, image=side_bar_button_image, text="", width=50, height=50,
                                        fg_color="#BB95E8", bg_color="#BB95E8", hover_color="#BB95E8",
                                        command=lambda: self.update_side_menu(side_menu_button, side_menu_frame))
        side_menu_button.place(x=0, y=0)
        side_menu_button.bind("<Enter>", lambda _: self.handle_side_button_hover(side_menu_button,
                                                                                 side_bar_button_hover_image))
        side_menu_button.bind("<Leave>", lambda _: self.handle_side_button_hover(side_menu_button,
                                                                                 side_bar_button_image))
        discord_token_entry = tk.CTkEntry(self.main_frame, placeholder_text="Discord Token", width=190, height=55,
                                          bg_color="#BB95E8", fg_color=self.LAVENDAR,
                                          placeholder_text_color="#000000", text_color="#000000",
                                          border_color=self.CAROUSEL_PINK)
        discord_token_entry.place(x=330, y=228)
        discord_login_button = tk.CTkButton(self.main_frame, text="Login", text_color="#000000", width=190, height=40,
                                            bg_color="#BB95E8", fg_color=self.LAVENDAR, hover_color=self.CAROUSEL_PINK,
                                            command=lambda: self.start_discord_client(discord_token_entry.get(), False,
                                                                                      False))
        discord_login_button.place(x=330, y=288)
        login_and_save_button = tk.CTkButton(self.main_frame, text="Login & Save", text_color="#000000", width=92,
                                             height=40, bg_color="#BB95E8", fg_color=self.LAVENDAR,
                                             hover_color=self.CAROUSEL_PINK,
                                             command=lambda: self.start_discord_client(discord_token_entry.get(), False,
                                                                                       True))
        login_and_save_button.place(x=330, y=333)
        quick_login_button = tk.CTkButton(self.main_frame, text="Quick Login", text_color="#000000", width=92,
                                          height=40, bg_color="#BB95E8", fg_color=self.LAVENDAR,
                                          hover_color=self.CAROUSEL_PINK,
                                          command=lambda: self.start_discord_client(discord_token_entry.get(), True,
                                                                                    False))
        quick_login_button.place(x=428, y=333)

        # BOTH PAGE HANDLER
        if not self.is_latest_version:
            latest_version_button = tk.CTkButton(side_menu_frame, text="Download Latest", width=190, height=40,
                                                 text_color="#000000", fg_color=self.LAVENDAR,
                                                 hover_color=self.CAROUSEL_PINK, command=self.handle_update)
            latest_version_button.place(x=5, y=140)
            messagebox.showinfo("New Version", "New version available, click the cloud button for download.")


if __name__ == '__main__':
    window = Window()
    window.main_screen()
    window.mainloop()
