import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk 
import os
import threading 
import time
from image_recognizer import ImageRecognizer
from config import ASSETS_DIR, PLACEHOLDER_IMAGE_PATH, LOADING_GIF_PATH, TOP_PREDICTIONS_COUNT

class ImageRecognitionApp:
    def __init__(self, master):
        self.master = master
        master.title("Amistad Görüntü Tanıma Uygulaması")
        master.geometry("800x700") 
        master.resizable(False, False) 

        self.recognizer = ImageRecognizer() 
        self.current_image_path = None 

        self._create_widgets() 
        self._load_placeholder_image() 

        self._check_model_loading_status()

    def _create_widgets(self):
        main_frame = tk.Frame(self.master, padx=10, pady=10)
        main_frame.pack(pady=10, fill="both", expand=True)

        self.image_display_label = tk.Label(main_frame, relief="solid", borderwidth=1)
        self.image_display_label.pack(pady=10)

        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)

        self.select_button = tk.Button(button_frame, text="Resim Seç", command=self.select_image)
        self.select_button.grid(row=0, column=0, padx=5)

        self.recognize_button = tk.Button(button_frame, text="Nesneyi Tanı", command=self.recognize_image)
        self.recognize_button.grid(row=0, column=1, padx=5)

        self.model_status_label = tk.Label(self.master, text="Model Yükleniyor...", fg="orange", font=("Helvetica", 10))
        self.model_status_label.pack(pady=5)
        
        self.loading_gif_label = tk.Label(self.master)
        self.loading_gif_label.pack(pady=5)
        self.loading_gif_label.pack_forget() 

        results_frame = tk.LabelFrame(self.master, text="Tahmin Sonuçları", padx=10, pady=10)
        results_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.results_text = tk.Text(results_frame, height=10, wrap="word", state="disabled", font=("Courier New", 12))
        self.results_text.pack(fill="both", expand=True)

    def _load_placeholder_image(self):
        if os.path.exists(PLACEHOLDER_IMAGE_PATH):
            try:
                img = Image.open(PLACEHOLDER_IMAGE_PATH)
                img = img.resize((300, 300), Image.Resampling.LANCZOS) 
                self.image_display_label.config(image=self.placeholder_photo)
                self.image_display_label.image = self.placeholder_photo 
                self.current_image_path = None
            except Exception as e:
                print(f"Yer tutucu resim yüklenirken hata: {e}")
                self.image_display_label.config(text="Resim Yüklenemedi")
        else:
            self.image_display_label.config(text="Yer Tutucu Resim Yok")
            print(f"Uyarı: Yer tutucu resim bulunamadı: {PLACEHOLDER_IMAGE_PATH}")

    def _show_loading_gif(self):
        if os.path.exists(LOADING_GIF_PATH):
            try:
                gif_frames = []
                img = Image.open(LOADING_GIF_PATH)
                for i in range(0, img.n_frames):
                    img.seek(i)
                    frame = img.copy().resize((50, 50), Image.Resampling.LANCZOS)
                    gif_frames.append(ImageTk.PhotoImage(frame))
                
                self.loading_frames = gif_frames
                self._animate_loading_gif(0)
                self.loading_gif_label.pack(pady=5)
            except Exception as e:
                print(f"Yükleniyor GIF'i yüklenirken hata: {e}")
                self.loading_gif_label.pack_forget()
        else:
            print(f"Uyarı: Yükleniyor GIF'i bulunamadı: {LOADING_GIF_PATH}")

    def _animate_loading_gif(self, frame_idx):
        if hasattr(self, 'loading_frames') and self.loading_gif_label.winfo_exists() and self.recognizer.model_loading:
            frame = self.loading_frames[frame_idx]
            self.loading_gif_label.config(image=frame)
            self.master.after(100, self._animate_loading_gif, (frame_idx + 1) % len(self.loading_frames))
        elif hasattr(self, 'loading_frames') and not self.recognizer.model_loading:
            self.loading_gif_label.pack_forget()


    def _check_model_loading_status(self):
        """Modelin yüklenme durumunu düzenli olarak kontrol eder ve GUI'yi günceller."""
        if self.recognizer.model_ready:
            self.model_status_label.config(text="Model Hazır", fg="green")
            self.select_button.config(state="normal")
            self.recognize_button.config(state="normal")
            self.loading_gif_label.pack_forget() 
       
        elif self.recognizer.model_loading:
            self.model_status_label.config(text="Model Yükleniyor...", fg="orange")
            self.select_button.config(state="disabled") 
            self.recognize_button.config(state="disabled")
            self._show_loading_gif() 
            self.master.after(1000, self._check_model_loading_status) 
        
        else: 
            self.model_status_label.config(text="Model Yüklenemedi! Lütfen konsolu kontrol edin.", fg="red")
            self.select_button.config(state="disabled")
            self.recognize_button.config(state="disabled")
            self.loading_gif_label.pack_forget()

    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Resim Seç",
            filetypes=[("Resim Dosyaları", "*.png *.jpg *.jpeg *.gif"), ("Tüm Dosyalar", "*.*")]
        )
        if file_path:
            self.current_image_path = file_path
            self._display_image(file_path)
            self._clear_results()
        
    def _display_image(self, image_path):
        """Seçilen resmi GUI'de gösterir."""
        try:
            img = Image.open(image_path)
            img.thumbnail((300, 300)) 
            self.photo = ImageTk.PhotoImage(img)
            self.image_display_label.config(image=self.photo)
            self.image_display_label.image = self.photo 
        except Exception as e:
            messagebox.showerror("Resim Yükleme Hatası", f"Resim yüklenirken bir hata oluştu: {e}")
            self._load_placeholder_image() 

    def recognize_image(self):
        if not self.current_image_path:
            messagebox.showwarning("Uyarı", "Lütfen önce bir resim seçin.")
            return

        if not self.recognizer.model_ready:
            messagebox.showwarning("Uyarı", "Model henüz yüklenmedi veya bir hata oluştu. Lütfen bekleyin veya uygulamayı yeniden başlatın.")
            return

        self._clear_results()
        self.results_text.config(state="normal")
        self.results_text.insert(tk.END, "Tahmin yapılıyor...\n")
        self.results_text.config(state="disabled")
        
        self._show_loading_gif()

        threading.Thread(target=self._run_recognition_task, args=(self.current_image_path,)).start()

    def _run_recognition_task(self, image_path):
    
        predictions = self.recognizer.predict_image(image_path)
    
        self.master.after(0, self._update_results_display, predictions)

    def _update_results_display(self, predictions):
      
        self.loading_gif_label.pack_forget() 

        self.results_text.config(state="normal") 
        self.results_text.delete(1.0, tk.END) 

        if predictions:
            self.results_text.insert(tk.END, "Tahmin Sonuçları:\n")
            for pred in predictions:
                self.results_text.insert(tk.END, f"- Nesne: {pred['label']}, Güvenilirlik: {pred['score']:.2f}\n")
        else:
            self.results_text.insert(tk.END, "Tahmin yapılamadı veya hiçbir nesne tanınmadı.\n"
                                        "Lütfen daha belirgin bir resim deneyin veya konsolu kontrol edin.")
        
        self.results_text.config(state="disabled") 

    def _clear_results(self):
        self.results_text.config(state="normal")
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state="disabled")

if __name__ == "__main__":
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR)
        print(f"'{ASSETS_DIR}' klasörü oluşturuldu.")
    
    if not os.path.exists(PLACEHOLDER_IMAGE_PATH):
        print(f"Uyarı: '{PLACEHOLDER_IMAGE_PATH}' bulunamadı. Lütfen 'assets' klasörüne bir 'placeholder.png' resmi ekleyin.")
        print("Uygulama çalışmaya devam edecek ancak yer tutucu resim görünmeyecektir.")
    
    if not os.path.exists(LOADING_GIF_PATH):
        print(f"Uyarı: '{LOADING_GIF_PATH}' bulunamadı. Lütfen 'assets' klasörüne bir 'loading.gif' dosyası ekleyin.")
        print("Yükleniyor animasyonu görünmeyecektir.")

    root = tk.Tk()
    app = ImageRecognitionApp(root)
    root.mainloop()

