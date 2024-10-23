# Author: Trolll, https://github.com/Trolll67, https://vk.com/trolll67
# Date: 2024-10-23
# Description: GUI tool for RMB/RAB to FBX converter
#
# License: GNU General Public License v3.0
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.


import configparser
import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox


def show_output_file(output_dir):
    try:
        if output_dir is None:
            messagebox.showerror("Error", "Could not process file!")
            return
        
        if not os.path.exists(output_dir):
            messagebox.showerror("Error", f"Output directory not found: {output_dir}")
            return
        
        messagebox.showinfo("Success", f"Output files saved to {output_dir}")
        subprocess.run(['explorer', output_dir.replace('/', '\\')])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open output directory: {e}")

def process_file(input_path, output_dir, all_in_one, rmb2blend, blend2fbx, mesh_only, anim_types):    
    os.makedirs(output_dir, exist_ok=True)

    root.grab_set()
    try:
        from converter import process
        result = process(input_path, output_dir, all_in_one, rmb2blend, blend2fbx, mesh_only, anim_types, False)
        if result and result.startswith("Error:"):
            messagebox.showerror("Error", result)
            return None
        return result
    except Exception as e:
        import traceback
        messagebox.showerror("Error", f"Could not process file: {e}")
        messagebox.showerror("Error", traceback.format_exc())
    finally:
        root.grab_release()

def open_file_dialog():
    file_path = filedialog.askopenfilename(title="Select a file")
    
    if file_path is None or file_path == "":
        return
    
    if not os.path.exists(file_path):
        messagebox.showerror("Error", "File not found")
        return
    
    output_dir = output_entry.get()
    all_in_one = all_in_one_var.get()
    rmb2blend = rmb2blend_var.get()
    blend2fbx = blend2fbx_var.get()
    mesh_only = mesh_only_var.get()
    anim_type = anim_type_entry.get() if use_anim_type_var.get() else "all"
    # polish anim_type
    anim_type = anim_type.replace(', ', ' ')
    anim_type = anim_type.replace(',', ' ')
    anim_types = anim_type.split(' ')

    # create output directory if not exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    out_dir = process_file(file_path, output_dir, all_in_one, rmb2blend, blend2fbx, mesh_only, anim_types)
    show_output_file(out_dir)

def select_output_directory():
    output_dir = filedialog.askdirectory(title="Select Output Directory")
    if output_dir:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, output_dir)

# ToolTip class
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        if self.tooltip_window:
            return
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)  # Remove window decorations (border, title)
        self.tooltip_window.wm_geometry(f"+{self.widget.winfo_rootx() + 20}+{self.widget.winfo_rooty() + 20}")

        label = tk.Label(self.tooltip_window, text=self.text, background="lightyellow", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class LargeToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.hide_tooltip_id = None
        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.on_widget_leave)

    def show_tooltip(self, event):
        if self.tooltip_window:
            return

        # Create the tooltip window without border decorations
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)

        # Set tooltip window position
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        # Create a frame to hold the text and the scrollbar
        frame = tk.Frame(self.tooltip_window, background="lightyellow", relief="solid", borderwidth=1)
        frame.pack()

        # Add a vertical scrollbar for long content
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a text widget for long text content
        text_widget = tk.Text(frame, height=10, width=50, wrap="word", background="lightyellow", relief="flat")
        text_widget.insert(tk.END, self.text)
        text_widget.config(state=tk.DISABLED)  # Make it read-only
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Link the scrollbar to the text widget
        text_widget.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=text_widget.yview)

        # Bind mouse events to keep tooltip open while interacting with it
        self.tooltip_window.bind("<Enter>", self.on_tooltip_enter)
        self.tooltip_window.bind("<Leave>", self.hide_tooltip)

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
            self.hide_tooltip_id = None

    def on_widget_leave(self, event):
        self.hide_tooltip_id = self.widget.after(200, self.hide_tooltip)

    def on_tooltip_enter(self, event):
        if self.hide_tooltip_id:
            self.widget.after_cancel(self.hide_tooltip_id)
            self.hide_tooltip_id = None

    def on_tooltip_leave(self, event):
        self.hide_tooltip_id = self.tooltip_window.after(200, self.hide_tooltip)

def download_blender_249():
    from converter import download_blender249
    download_blender249(download_status)

def download_blender_36():
    from converter import download_blender36
    download_blender36(download_status) 

def start_download():
    cli_path = os.path.join(os.path.dirname(os.path.abspath(sys.executable)), 'converter_cli.exe')
    if not os.path.exists(cli_path):
        messagebox.showerror("Error", f"converter_cli.exe not found! {cli_path}")
        sys.exit(1)

    # run cli with arguments
    command = ['cmd', '/c', 'start', 'cmd', '/k', cli_path, '--download-blender']
    subprocess.Popen(command, shell=True)
    messagebox.showinfo("Info", "Downloading started. Please wait until it finishes.")

def toggle_anim_type_entry(*args):
    if use_anim_type_var.get():
        anim_type_entry.config(state=tk.NORMAL)
    else:
        anim_type_entry.config(state=tk.DISABLED)


root = tk.Tk()
root.title("RMB/RAB to FBX Converter GUI Tool v1.0")
root.geometry("400x300")

output_label = tk.Label(root, text="Output Directory:")
output_label.pack(pady=(20, 5))

output_frame = tk.Frame(root)
output_frame.pack(pady=5)

output_entry = tk.Entry(output_frame, width=50)
output_entry.pack(side=tk.LEFT, padx=(0, 5))
output_entry.insert(0, os.path.join(os.path.dirname(os.path.abspath(sys.executable)), "output_models"))

output_button = tk.Button(output_frame, text="Browse", command=select_output_directory)
output_button.pack(side=tk.LEFT)

option_frame = tk.Frame(root)
option_frame.pack(pady=10)

all_in_one_var = tk.BooleanVar()
rmb2blend_var = tk.BooleanVar(value=True)
blend2fbx_var = tk.BooleanVar(value=True)
mesh_only_var = tk.BooleanVar()

all_in_one_check = tk.Checkbutton(option_frame, text="All in One", variable=all_in_one_var)
all_in_one_check.pack(side=tk.LEFT, padx=5)

rmb2blend_check = tk.Checkbutton(option_frame, text="RMB to Blend", variable=rmb2blend_var)
rmb2blend_check.pack(side=tk.LEFT, padx=5)

blend2fbx_check = tk.Checkbutton(option_frame, text="Blend to FBX", variable=blend2fbx_var)
blend2fbx_check.pack(side=tk.LEFT, padx=5)

mesh_only_check = tk.Checkbutton(option_frame, text="Mesh Only", variable=mesh_only_var)
mesh_only_check.pack(side=tk.LEFT, padx=5)

anim_type_frame = tk.Frame(root)
anim_type_frame.pack(pady=10)

# Animation Type
use_anim_type_var = tk.BooleanVar(value=False)
use_anim_type_var.trace_add("write", toggle_anim_type_entry)

use_anim_type_check = tk.Checkbutton(anim_type_frame, text="Use Animation Type", variable=use_anim_type_var)
use_anim_type_check.pack(side=tk.LEFT, padx=(0, 5))

anim_type_entry = tk.Entry(anim_type_frame, width=15)
anim_type_entry.insert(0, "all")
anim_type_entry.pack(side=tk.LEFT)
toggle_anim_type_entry()

available_anim_types_tip = "ATTACK1 ATTACK2 WALK DEAD etc."
available_anim_types = ['ATTACK1', 'ATTACK2', 'ATTACK_COMBO1', 'ATTACK_COMBO2', 'ATTACK_COMBO3', 
                        'ATTACK_COMBO4', 'ATTACK_COMBO5', 'ATTACK_COMBO5_1', 'ATTACK_COMBO6', 
                        'ATTACK_COMBO7', 'ATTACK_COMBO8', 'ATTACK_COMBO8_1', 'ATTACK_STRONG1', 
                        'BATTLE_STAND', 'BATTLE_STAND_TO_WEAPON_STAND', 'CONDITION', 'CONDITION_IDLE', 
                        'DAMAGE_DOWN', 'DAMAGE_DOWNNOWEAPON', 'DAMAGE_LEFT', 'DAMAGE_LEFTNOWEAPON', 
                        'DAMAGE_RIGHT', 'DAMAGE_RIGHTNOWEAPON', 'DAMAGE_UP', 'DAMAGE_UPNOWEAPON', 
                        'DEAD', 'DOWN', 'IDLE', 'IDLE1', 'IDLE2', 'IDLE3', 'ITEM_PICKUP', 
                        'LEVITATE_BACK', 'LEVITATE_BACK_ON_THE_WATER', 'LEVITATE_FORWARD', 
                        'LEVITATE_FORWARD_ON_THE_WATER', 'LEVITATE_IDLE', 'LEVITATE_IDLE_ON_THE_WATER', 
                        'MOVINGATTACK', 'ONTHEWATER_NOWEAPON', 'ON_THE_WATER', 'REGEN', 'REGENORSAY', 
                        'RUN', 'RUNNOWEAPON', 'RUN_FORWARD_LEFT', 'RUN_FORWARD_RIGHT', 'RUN_LEFT', 
                        'RUN_RIGHT', 'SAY', 'SITDOWN', 'SITDOWN_START', 'SKILL', 'SKILL1', 'SKILL10', 
                        'SKILL11', 'SKILL12', 'SKILL13', 'SKILL14', 'SKILL15', 'SKILL2', 'SKILL3', 
                        'SKILL4', 'SKILL5', 'SKILL6', 'SKILL7', 'SKILL8', 'SKILL9', 'SKILL_RUN', 
                        'SKILL_WALK_BACK', 'SLEEP', 'SPELL', 'SPRINT', 'SPRINT_FORWARD_LEFT', 
                        'SPRINT_FORWARD_RIGHT', 'SPRINT_LEFT', 'SPRINT_RIGHT', 'STAND1', 'STAND2', 
                        'STANDUP_START', 'STAND_FALL', 'STAND_FALLNOWEAPON', 'STAND_JUMP', 
                        'STAND_JUMPNOWEAPON', 'STAND_LAND', 'STAND_LANDNOWEAPON', 'STAND_TAKING', 
                        'SWIM', 'SWIMMING_NOWEAPON', 'SWIM_BACK', 'TAKING', 'THROW', 'TURN_LEFT', 
                        'TURN_RIGHT', 'USE_STICK', 'VICTORY', 'WALK', 'WALK_BACK', 'WALK_BACKNOWEAPON', 
                        'WALK_BACK_LEFT', 'WALK_BACK_RIGHT', 'WALK_FORWARD_LEFT', 'WALK_FORWARD_RIGHT', 
                        'WALK_LEFT', 'WALK_RIGHT', 'WALK_TAKING', 'WEAPON_PUTIN', 'WEAPON_STAND']

ToolTip(anim_type_entry, f"Animation types (you can enter multiple values separated by spaces): {available_anim_types_tip}")

anim_help_label = tk.Label(anim_type_frame, text="?", cursor="hand2", font=("Arial", 10, "bold"))
anim_help_label.pack(side=tk.LEFT, padx=(5, 0))
LargeToolTip(anim_help_label, "All available animation types:\n" + "\n".join(available_anim_types))

open_button = tk.Button(root, text="Open File", command=open_file_dialog, width=20, bg='#0077b6', fg='#FFFFFF')
open_button.pack(pady=(30, 10))

author_label = tk.Label(root, text="Created by Trolll", wraplength=300, fg="#003049", cursor="hand2")
author_label.pack(side=tk.BOTTOM, pady=10)

def open_link(event):
    import webbrowser
    webbrowser.open("https://github.com/Trolll67")

author_label.bind("<Button-1>", open_link)

# check config file
config_path = 'config.ini'
config = configparser.ConfigParser()
if not os.path.exists(config_path):
    config['Blender'] = {
        'blender_249_path': '',
        'blender_36_path': ''
    }

    with open(config_path, 'w') as configfile:
        config.write(configfile)

# check if blenders exist
config.read(config_path)
blender_249_path = config['Blender']['blender_249_path']
blender_36_path = config['Blender']['blender_36_path']

if not os.path.exists(blender_249_path):
    messagebox.showwarning("Warning", "Blender 2.49b not found! Please set the path in config.ini")
    if messagebox.askyesno("Blender 2.49", "Do you want to download Blender 2.49 and set the path?"):
        start_download()
    else:
        sys.exit(1)

if not os.path.exists(blender_36_path):
    messagebox.showwarning("Warning", "Blender 3.6 not found! Please set the path in config.ini")
    if messagebox.askyesno("Blender 3.6", "Do you want to download Blender 3.6 and set the path?"):
        start_download()
    else:
        sys.exit(1)

root.mainloop()