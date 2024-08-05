
import os
import cv2
import numpy as np
import argparse
import warnings
import time

from src.anti_spoof_predict import AntiSpoofPredict
from src.generate_patches import CropImage
from src.utility import parse_model_name
warnings.filterwarnings('ignore')
class realORfake:
    def test_live(model_dir, device_id,frame):
        model_test = AntiSpoofPredict(device_id)
        image_cropper = CropImage()
        
        while True:
        
            image_bbox = model_test.get_bbox(frame)
            prediction = np.zeros((1, 3))
            
            for model_name in os.listdir(model_dir):
                h_input, w_input, model_type, scale = parse_model_name(model_name)
                param = {
                    "org_img": frame,
                    "bbox": image_bbox,
                    "scale": scale,
                    "out_w": w_input,
                    "out_h": h_input,
                    "crop": True,
                }
                if scale is None:
                    param["crop"] = False
                img = image_cropper.crop(**param)
                prediction += model_test.predict(img, os.path.join(model_dir, model_name))

            label = np.argmax(prediction)
            value = prediction[0][label] / 2
            if label == 1:
                #print("Real Face. Score: {:.2f}.".format(value))
                result_text = "RealFace Score: {:.2f}".format(value)
                color = (255, 0, 0)
                return True
            else:
                #print("Fake Face. Score: {:.2f}.".format(value))
                result_text = "FakeFace Score: {:.2f}".format(value)
                color = (0, 0, 255)
                return False

            # cv2.rectangle(
            #     frame,
            #     (image_bbox[0], image_bbox[1]),
            #     (image_bbox[0] + image_bbox[2], image_bbox[1] + image_bbox[3]),
            #     color, 2)
            # cv2.putText(
            #     frame,
            #     result_text,
            #     (image_bbox[0], image_bbox[1] - 5),
            #     cv2.FONT_HERSHEY_COMPLEX, 0.5 * frame.shape[0] / 1024, color)

    #   cv2.imshow("Live Face Detection", frame)

        
    #    cv2.destroyAllWindows()
    def start(frame):
        desc = "test"
        parser = argparse.ArgumentParser(description=desc)
        parser.add_argument(
            "--device_id",
            type=int,
            default=0,
            help="which gpu id, [0/1/2/3]")
        parser.add_argument(
            "--model_dir",
            type=str,
            default="./resources/anti_spoof_models",
            help="model_lib used to test")
        args = parser.parse_args()
        result = realORfake.test_live(args.model_dir, args.device_id,frame)
        return result