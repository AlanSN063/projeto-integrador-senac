"""Ícones vetoriais desenhados com Pillow; não dependem de emojis ou fontes especiais."""
from functools import lru_cache
from PIL import Image, ImageDraw
import customtkinter as ctk

@lru_cache(maxsize=256)
def get_icon(name, color="#FFFFFF", size=20):
    scale=4
    im=Image.new("RGBA",(24*scale,24*scale),(0,0,0,0))
    d=ImageDraw.Draw(im)
    def line(points, width=2):
        d.line([(int(x*scale),int(y*scale)) for x,y in points],fill=color,width=width*scale,joint="curve")
    def rect(box, radius=0):
        b=tuple(int(v*scale) for v in box)
        d.rounded_rectangle(b,radius=radius*scale,outline=color,width=2*scale)
    def circle(box, fill=None):
        d.ellipse(tuple(int(v*scale) for v in box),outline=color,fill=fill,width=2*scale)
    if name=="home":
        line([(3,11),(12,3),(21,11)]);line([(5,10),(5,21),(19,21),(19,10)])
    elif name in ("package","boxes"):
        line([(3,7),(12,3),(21,7),(21,17),(12,21),(3,17),(3,7)]);line([(3,7),(12,12),(21,7)]);line([(12,12),(12,21)])
    elif name=="truck":
        rect((2,5,15,17));line([(15,9),(19,9),(22,13),(22,17),(15,17)]);circle((5,16,9,20));circle((17,16,21,20))
    elif name=="tags":
        line([(3,4),(13,4),(21,12),(12,21),(3,12),(3,4)]);circle((6,7,8,9))
    elif name=="wrench":
        line([(14,5),(17,2),(21,3),(22,7),(19,10),(16,10),(8,18)]);circle((4,17,8,21));line([(8,18),(15,11)])
    elif name=="arrows":
        line([(3,8),(21,8),(17,4)]);line([(21,8),(17,12)]);line([(21,16),(3,16),(7,12)]);line([(3,16),(7,20)])
    elif name=="users":
        circle((8,3,16,11));d.arc((3*scale,12*scale,21*scale,23*scale),180,360,fill=color,width=2*scale)
    elif name=="chart":
        line([(3,3),(3,21),(22,21)]);rect((6,12,9,18));rect((12,8,15,18));rect((18,5,21,18))
    elif name=="settings":
        circle((8,8,16,16));circle((3,3,21,21));line([(12,1),(12,4)]);line([(12,20),(12,23)]);line([(1,12),(4,12)]);line([(20,12),(23,12)])
    elif name=="lock":
        rect((5,10,19,21),2);d.arc((7*scale,2*scale,17*scale,15*scale),180,360,fill=color,width=2*scale)
    elif name=="search":
        circle((3,3,15,15));line([(14,14),(21,21)])
    elif name=="eye":
        line([(2,12),(6,8),(12,6),(18,8),(22,12),(18,16),(12,18),(6,16),(2,12)]);circle((10,10,14,14))
    elif name=="edit":
        line([(4,19),(7,15),(17,5),(20,8),(10,18),(4,19)]);line([(14,8),(17,11)])
    elif name=="trash":
        rect((6,7,18,21),1);line([(4,6),(20,6)]);line([(9,3),(15,3)]);line([(10,10),(10,18)]);line([(14,10),(14,18)])
    elif name=="logout":
        line([(10,4),(4,4),(4,20),(10,20)]);line([(10,12),(22,12),(17,7)]);line([(22,12),(17,17)])
    else:
        circle((5,5,19,19))
    im=im.resize((size,size),Image.Resampling.LANCZOS)
    return ctk.CTkImage(light_image=im,dark_image=im,size=(size,size))
