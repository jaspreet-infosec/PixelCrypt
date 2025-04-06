import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import customtkinter as ctk

# Initialize CustomTkinter
ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")


def browse_image():
    global img_path
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        img_path = file_path
        display_image(file_path)


def display_image(file_path):
    image = Image.open(file_path)
    image = image.resize((400, 400))
    img = ctk.CTkImage(light_image=image, dark_image=image, size=(400, 400))
    panel.configure(image=img)
    panel.image = img


def encode_text():
    if not img_path:
        messagebox.showerror("Error", "Please select an image first!")
        return
    text_entry.pack(pady=10)
    encode_btn.configure(command=process_encoding)


def process_encoding():
    text = text_entry.get("1.0", tk.END).strip()
    if text:
        image = cv2.imread(img_path)
        encoded_img = hide_text(image, text)
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
        if save_path:
            cv2.imwrite(save_path, encoded_img)
            messagebox.showinfo("Success", "Text hidden and image saved!")


def decode_text():
    if not img_path:
        messagebox.showerror("Error", "Please select an image first!")
        return
    image = cv2.imread(img_path)
    hidden_text = extract_text(image)
    messagebox.showinfo("Hidden Text", f"Extracted Message: {hidden_text}")


def hide_text(image, text):
    binary_text = ''.join(format(ord(c), '08b') for c in text) + '1111111111111110'
    data_index = 0
    img_shape = image.shape

    for row in range(img_shape[0]):
        for col in range(img_shape[1]):
            for channel in range(3):
                if data_index < len(binary_text):
                    new_value = (int(image[row, col, channel]) & ~1) | int(binary_text[data_index])
                    image[row, col, channel] = np.uint8(new_value)
                    data_index += 1
                else:
                    return image
    return image


def extract_text(image):
    binary_text = ""
    for row in image:
        for pixel in row:
            for channel in range(3):
                binary_text += str(pixel[channel] & 1)

    chars = [binary_text[i:i + 8] for i in range(0, len(binary_text), 8)]
    message = ""
    for c in chars:
        char = chr(int(c, 2))
        if message.endswith("\xFE"):
            break
        message += char

    return message.rstrip("\xFE")


# GUI Setup
root = ctk.CTk()
root.title("Steganography Tool")
root.geometry("700x800")
root.resizable(False, False)

frame = ctk.CTkFrame(root)
frame.pack(pady=20, padx=20, fill="both", expand=True)

title = ctk.CTkLabel(frame, text="Image Steganography", font=("Arial", 20, "bold"))
title.pack(pady=10)

panel = ctk.CTkLabel(frame, text="No Image Selected", width=400, height=400, corner_radius=10,
                     fg_color=("gray20", "gray25"))
panel.pack(pady=10)

text_entry = ctk.CTkTextbox(frame, width=400, height=100)
text_entry.insert("1.0", "Enter text here...")
text_entry.pack_forget()

browse_btn = ctk.CTkButton(frame, text="Browse Image", command=browse_image)
browse_btn.pack(pady=5)

encode_btn = ctk.CTkButton(frame, text="Encode Text", command=encode_text, fg_color="red")
encode_btn.pack(pady=5)

decode_btn = ctk.CTkButton(frame, text="Decode Text", command=decode_text, fg_color="blue")
decode_btn.pack(pady=5)

exit_btn = ctk.CTkButton(frame, text="Exit", fg_color="red", command=root.quit)
exit_btn.pack(pady=5)

img_path = ""
root.mainloop()
