import os
import shutil
from ensemble import EnsembleModel
import pandas as pd



def classify_images(current_folder, classified_folder_path, confidence_threshold):
    deer_path = os.path.join(classified_folder_path, 'Олень')
    musk_deer_path = os.path.join(classified_folder_path, 'Кабарга')
    roe_deer_path = os.path.join(classified_folder_path, 'Косуля')
    uncertain_path = os.path.join(classified_folder_path, 'Низкая уверенность')

    ensemble_model = EnsembleModel(alpha=0.5, confidence=confidence_threshold)
    data = []
    try:
        for path in [classified_folder_path, deer_path, musk_deer_path, roe_deer_path, uncertain_path]:
            if not os.path.exists(path):
                os.makedirs(path)

        for file_name in os.listdir(current_folder):
            file_path = os.path.join(current_folder, file_name)
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                continue

            print(file_path)
            final_class = ensemble_model.predict(file_path)
            model_names = {0: 'Олень', 1: 'Кабарга', 2: 'Косуля'}
            for_csv = {'Кабарга': 0, 'Косуля': 1, 'Олень': 2}
            print(f"Final Prediction: {model_names[final_class]}")

            data.append({'img_name': file_name, 'class':for_csv[model_names[final_class]]})

            if final_class == 0:
                shutil.copy(file_path, deer_path)
            elif final_class == 1:
                shutil.copy(file_path, musk_deer_path)
            elif final_class == 2:
                shutil.copy(file_path, roe_deer_path)
            else:
                shutil.copy(file_path, uncertain_path)

        df = pd.DataFrame(data, columns=['img_name', 'class'])

        df.to_csv('result.csv', index=False)

    except Exception as e:
        print(f"Error during classification: {e}")
    finally:
        return [deer_path, musk_deer_path, roe_deer_path, uncertain_path]
