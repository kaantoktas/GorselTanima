import os 
MODEL_NAME = "MobileNetV2" 
IMAGE_TARGET_SIZE = (224, 224)
TOP_PREDICTIONS_COUNT = 5
ASSETS_DIR = "assets/"
PLACEHOLDER_IMAGE_PATH = os.path.join(ASSETS_DIR, "placeholder.png")
LOADING_GIF_PATH = os.path.join(ASSETS_DIR, "loading.gif")
