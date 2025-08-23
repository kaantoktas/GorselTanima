import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.applications.resnet50 import ResNet50
from tensorflow.keras.applications.inception_v3 import InceptionV3
import numpy as np
import os
from PIL import Image
import threading 

from config import MODEL_NAME, IMAGE_TARGET_SIZE, TOP_PREDICTIONS_COUNT

class ImageRecognizer:
    def __init__(self):
        self.model = None
        self.model_ready = False
        self.model_loading = False
        self._load_model_in_background() 

    def _load_model_in_background(self):
   
        if self.model_loading:
            return

        self.model_loading = True
        print(f"[{MODEL_NAME}] modeli yükleniyor... Bu biraz zaman alabilir.")
        
        def load_model_task():
            try:
                if MODEL_NAME == "MobileNetV2":
                    self.model = MobileNetV2(weights='imagenet')
                elif MODEL_NAME == "VGG16":
                    self.model = VGG16(weights='imagenet')
                elif MODEL_NAME == "ResNet50":
                    self.model = ResNet50(weights='imagenet')
                elif MODEL_NAME == "InceptionV3":
                    self.model = InceptionV3(weights='imagenet')
                else:
                    raise ValueError(f"Desteklenmeyen MODEL_NAME: {MODEL_NAME}")
                
                self.model_ready = True
                print(f"[{MODEL_NAME}] modeli başarıyla yüklendi.")
            except Exception as e:
                print(f"Hata: [{MODEL_NAME}] modeli yüklenirken bir sorun oluştu: {e}")
                self.model_ready = False
            finally:
                self.model_loading = False

        threading.Thread(target=load_model_task, daemon=True).start()


    def preprocess_image(self, image_path):
        """
        Görüntüyü modele uygun hale getirmek için ön işler.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Görüntü dosyası bulunamadı: {image_path}")

        try:
            img = Image.open(image_path).resize(IMAGE_TARGET_SIZE)
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            if MODEL_NAME == "MobileNetV2":
                return preprocess_input(img_array)
            elif MODEL_NAME in ["VGG16", "ResNet50", "InceptionV3"]:
                return tf.keras.applications.imagenet_utils.preprocess_input(img_array)
            else:
                return img_array 
        except Exception as e:
            raise Exception(f"Görüntü ön işlenirken hata oluştu: {e}")

    def predict_image(self, image_path):
  
        if not self.model_ready:
            print("Model henüz yüklenmedi veya bir hata oluştu. Lütfen bekleyin veya uygulamayı yeniden başlatın.")
            return [] 

        try:
            processed_image = self.preprocess_image(image_path)
            predictions = self.model.predict(processed_image)
            
            decoded_predictions = decode_predictions(predictions, top=TOP_PREDICTIONS_COUNT)[0]

            results = []
            for i, (imagenet_id, label, score) in enumerate(decoded_predictions):
                results.append({
                    "label": label.replace('_', ' ').capitalize(), 
                    "score": float(score) 
                })
            return results
        except FileNotFoundError as e:
            print(f"Görüntü tanıma hatası: {e}")
            return []
        except Exception as e:
            print(f"Görüntü tanıma sırasında beklenmedik bir hata oluştu: {e}")
            return []

if __name__ == "__main__":
    recognizer = ImageRecognizer()

    while not recognizer.model_ready:
        print("Model yükleniyor, lütfen bekleyin...")
        time.sleep(2) 

    test_image_path = os.path.join("assets", "test_image.jpg") 

    if not os.path.exists(test_image_path):
        print(f"\nUyarı: '{test_image_path}' bulunamadı. Lütfen 'assets' klasörüne bir test resmi ekleyin.")
        print("Örn: assets/kedi.jpg, assets/araba.png")
    else:
        print(f"\n'{test_image_path}' üzerinde tahmin yapılıyor...")
        predictions = recognizer.predict_image(test_image_path)

        if predictions:
            print("Tahmin Sonuçları:")
            for pred in predictions:
                print(f"- Nesne: {pred['label']}, Güvenilirlik: {pred['score']:.2f}")
        else:
            print("Tahmin yapılamadı veya hiçbir nesne tanınmadı.")

