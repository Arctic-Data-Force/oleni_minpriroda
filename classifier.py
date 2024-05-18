import os
import shutil

def classify_images(current_folder, classified_folder_path, confidence_threshold):
    deer_path = os.path.join(classified_folder_path, 'Олень')
    musk_deer_path = os.path.join(classified_folder_path, 'Кабарга')
    roe_deer_path = os.path.join(classified_folder_path, 'Косуля')
    uncertain_path = os.path.join(classified_folder_path, 'Низкая уверенность')

    try:
        for path in [classified_folder_path, deer_path, musk_deer_path, roe_deer_path, uncertain_path]:
            if not os.path.exists(path):
                os.makedirs(path)

        for index in range(len(os.listdir(current_folder))):
            file_path = os.path.join(current_folder, f"img_{index}.png")
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                continue
            # Insert classification logic here
            # Example:
            # result, confidence = classify_image(file_path)
            # Placeholder for classification result and confidence
            result = 'Олень'
            confidence = 0.95
            if confidence < confidence_threshold:
                shutil.copy(file_path, uncertain_path)
            else:
                if result == 'Олень':
                    shutil.copy(file_path, deer_path)
                elif result == 'Кабарга':
                    shutil.copy(file_path, musk_deer_path)
                elif result == 'Косуля':
                    shutil.copy(file_path, roe_deer_path)
    except Exception as e:
        print(f"Error during classification: {e}")
    finally:
        return [deer_path, musk_deer_path, roe_deer_path, uncertain_path]
