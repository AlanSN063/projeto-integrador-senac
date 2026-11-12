import customtkinter as ctk

# Paleta principal solicitada: vermelho, vinho, grafite e carvão.
COLORS = {
    "red": "#FF0000", "dark_red": "#AF0404",
    "graphite": "#414141", "charcoal": "#252525",
    "navy": "#252525", "blue": "#FF0000", "blue_hover": "#AF0404",
    "background": "#F5F5F5", "white": "#FFFFFF",
    "text": "#252525", "muted": "#626262", "border": "#DEDEDE",
    "green": "#414141", "orange": "#AF0404", "purple": "#252525",
    "sidebar_hover": "#414141", "table_header": "#ECECEC",
    "soft_red": "#FFE3E3", "soft_gray": "#EEEEEE",
}

FONTS = {
    "title": ("Poppins", 22, "bold"),
    "subtitle": ("Poppins", 14, "normal"),
    "body": ("Roboto", 13, "normal"),
    "small": ("Roboto", 11, "normal"),
    "button": ("Roboto", 13, "bold"),
    "metric": ("Poppins", 25, "bold"),
}

def configure_appearance():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")  # Os botões recebem cores explícitas da paleta.
