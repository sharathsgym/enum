from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import requests
import cv2
import numpy as np

# load image from the IAM database
url = 'https://uploadedpics.blob.core.windows.net/charts/96aafdf2-e2f2-447e-bf9e-a44d4f6dc494'
image = Image.open(requests.get(url, stream=True).raw).convert("RGB")
image_np = np.array(image)

r = image_np[570:664, 440:630]
cv2.imshow('ques_index', r)
cv2.waitKey(0)  # Wait until any key is pressed
cv2.destroyAllWindows()
input("press")

processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-handwritten')
model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-handwritten')
pixel_values = processor(images=r, return_tensors="pt").pixel_values

generated_ids = model.generate(pixel_values)
generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]



print(generated_text)