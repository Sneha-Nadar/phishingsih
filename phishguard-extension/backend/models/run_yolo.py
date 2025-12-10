from ultralytics import YOLO

model = YOLO('yolov8n.pt')
results = model.predict('C:/Users/Sneha\'s Leno/phishingsih/phishguard-extension/backend/models/abodedublin.com_122.png', imgsz=640, save=True)
print(results)
