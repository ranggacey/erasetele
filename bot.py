import os
import cv2
from rembg import remove
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from PIL import Image
import numpy as np

# Fungsi untuk menghapus latar belakang gambar
def remove_background(image_path, output_path):
    try:
        with open(image_path, 'rb') as input_file:
            input_data = input_file.read()
            output_data = remove(input_data)
        with open(output_path, 'wb') as output_file:
            output_file.write(output_data)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

# Fungsi untuk menghapus latar belakang dari setiap frame dalam video
def remove_background_from_video(input_video_path, output_video_path):
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        print("Error: Tidak dapat membuka video.")
        return False

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Menentukan codec video untuk output
    out = cv2.VideoWriter(output_video_path, fourcc, 30.0, (int(cap.get(3)), int(cap.get(4))))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Mengubah frame ke format PIL untuk diolah oleh rembg
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        pil_image.save("frame.jpg")
        remove_background("frame.jpg", "frame_no_bg.png")

        # Baca gambar hasil pengolahan dan gabungkan ke dalam video
        result_image = Image.open("frame_no_bg.png")
        result_frame = np.array(result_image)
        result_frame = cv2.cvtColor(result_frame, cv2.COLOR_RGB2BGR)

        # Menulis frame ke video output
        out.write(result_frame)

    cap.release()
    out.release()
    os.remove("frame.jpg")
    os.remove("frame_no_bg.png")
    return True

# Fungsi untuk menangani foto yang diunggah
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    input_path = f"{user.id}_input.jpg"
    output_path = f"{user.id}_output.png"

    # Unduh foto dari pengguna
    await photo_file.download_to_drive(input_path)
    await update.message.reply_text("Menghapus latar belakang gambar, tunggu cuy")

    # Proses menghapus latar belakang
    if remove_background(input_path, output_path):
        # Kirim gambar hasil ke pengguna
        await update.message.reply_photo(photo=open(output_path, 'rb'))
        # Hapus file sementara
        os.remove(input_path)
        os.remove(output_path)
    else:
        await update.message.reply_text("Eror jir. Silakan coba lagi.")

# Fungsi untuk menangani video yang diunggah
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    video_file = await update.message.video.get_file()
    input_video_path = f"{user.id}_input.mp4"
    output_video_path = f"{user.id}_output.mp4"

    # Unduh video dari pengguna
    await video_file.download_to_drive(input_video_path)
    await update.message.reply_text("Menghapus latar belakang video, tunggu cik")

    # Proses menghapus latar belakang video
    if remove_background_from_video(input_video_path, output_video_path):
        # Kirim video hasil ke pengguna
        await update.message.reply_video(video=open(output_video_path, 'rb'))
        # Hapus file sementara
        os.remove(input_video_path)
        os.remove(output_video_path)
    else:
        await update.message.reply_text("Gagal jir. Silakan coba lagi.")

# Fungsi untuk perintah /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Kirimkan foto atau video, dan saya akan menghapus latar belakangnya untuk Anda.")

# Fungsi utama untuk menjalankan bot
def main():
    TOKEN = "7548424575:AAG_49RK9lgh5d-bwXPZRHFWPdlN5mWCI6g"  # Ganti dengan token bot Anda

    # Gunakan Application sebagai pengganti Updater
    application = Application.builder().token(TOKEN).build()

    # Tambahkan handler untuk perintah /start
    application.add_handler(CommandHandler("start", start))

    # Tambahkan handler untuk menangani foto
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Tambahkan handler untuk menangani video
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))

    # Jalankan bot
    print("Bot sedang berjalan...")
    application.run_polling()

if __name__ == "__main__":
    main()
