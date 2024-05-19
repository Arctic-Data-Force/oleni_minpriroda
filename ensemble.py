import numpy as np
from collections import Counter
from ultralytics import YOLO


def detect_objects_and_get_probs(detection_model, image, confidence=0.7):
    detections = detection_model.predict(image)
    class_probs = []

    for conf, cls in zip(detections[0].boxes.conf.cpu(), detections[0].boxes.cls.cpu()):
        if conf > confidence:
            # Создаем массив вероятностей для каждого класса
            prob = np.zeros(len(detection_model.names))
            prob[int(cls)] = conf
            class_probs.append(prob)

    # Усредняем вероятности классов для всех обнаруженных объектов
    if class_probs:
        avg_class_probs = np.mean(class_probs, axis=0)
    else:
        avg_class_probs = np.zeros(len(detection_model.names))

    return avg_class_probs


class ObjectDetectionModel:
    def __init__(self, model_paths, confidence):
        self.models = [self.load_model(path) for path in model_paths]
        self.confidence = confidence

    def load_model(self, model_path):
        model = YOLO(model_path, verbose=False)
        model.fuse()
        return model

    def detect(self, image):
        all_class_probs = []
        for model in self.models:
            class_probs = detect_objects_and_get_probs(model, image)
            all_class_probs.append(class_probs)
        # Усредняем вероятности классов для всех моделей
        avg_class_probs = np.mean(all_class_probs, axis=0)
        return avg_class_probs


class ClassifierModel:
    def __init__(self, model_paths):
        self.models = [self.load_model(path) for path in model_paths]

    def load_model(self, model_path):
        model = YOLO(model_path, verbose=False)
        model.fuse()
        return model

    def extract_probs(self, result):
        # Предполагается, что результат содержит атрибут probs с вероятностями классов
        return result.probs.data.cpu().detach().numpy()

    def predict(self, images):
        all_predictions = []
        for image in images:
            model_predictions = []
            for model in self.models:
                result = model.predict(image)
                preds = self.extract_probs(result[0])  # Извлекаем вероятности классов из объекта Results
                model_predictions.append(preds)
            avg_prediction = np.mean(model_predictions, axis=0)
            all_predictions.append(avg_prediction)
        return all_predictions


class EnsembleModel:
    def __init__(self, alpha=0.5, confidence=0.7):
        self.od_model = ObjectDetectionModel(["weights/yolov8s_640_10ep_16b.pt","weights/yolov8m_640_30ep_16b.pt"], confidence)
        self.clf_model = ClassifierModel(["weights/yolov8m-cls-50ep-16b.pt", "weights/yolov8x-cls-30ep-16b.pt", "weights/yolov8x-cls_640_10ep.pt"])
        self.alpha = alpha

    def ensemble_predictions(self, od_probs, clf_probs):
        # Усреднение вероятностей с весовым коэффициентом alpha
        ensemble_prob = self.alpha * od_probs + (1 - self.alpha) * clf_probs
        return ensemble_prob

    def final_prediction(self, ensemble_probs):
        final_class = np.argmax(ensemble_probs)
        return final_class

    def predict(self, image):
        # Получение усреднённых вероятностей классов от моделей Object Detection
        od_probs = self.od_model.detect(image)

        # Классификация объектов
        clf_probs = self.clf_model.predict([image])[0]

        # Объединение результатов
        ensemble_probs = self.ensemble_predictions(od_probs, clf_probs)

        # Финальное предсказание
        final_class = self.final_prediction(ensemble_probs)
        return final_class


if __name__ == "__main__":
    # Пример использования
    # od_model_paths = ["weights/yolov8s_640_10ep_16b.pt", "weights/yolov8m_640_30ep_16b.pt"]  # "weights/yolov9c_640_20ep.pt",   Пути к моделям Object Detection
    # clf_model_paths = ["weights/yolov8m-cls-50ep-16b.pt", "weights/yolov8x-cls-30ep-16b.pt", "weights/yolov8x-cls_640_10ep.pt"]  # Пути к классификаторам

    # image = load_image("path_to_image.jpg")  # Функция загрузки изображения
    image = "test_data/Im_0002350_1_jpg.rf.0b1232557814e2a273d91197a49731e8.jpg"
    ensemble_model = EnsembleModel(alpha=0.5, confidence=0.8)
    final_class = ensemble_model.predict(image)
    model_names = {0: 'deer', 1: 'muskdeer', 2: 'roe'}
    print(f"Final Prediction: {model_names[final_class]}")
