import os
import numpy as np
import tensorflow as tf
from PIL import Image
import matplotlib.pyplot as plt
from tensorflow.keras.applications.vgg19 import VGG19, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing.image import load_img, img_to_array

def main():
    # Caminho para o diretório de treinamento e teste
    train_dir = 'fruits-360-original-size/Training'
    test_dir = 'fruits-360-original-size/Test'

    # Obter a lista de classes (nomes das pastas)
    class_names = sorted(os.listdir(train_dir))
    print(class_names)

    num_class = len(class_names)

    for root, dirs, files in os.walk("fruits-360-original-size/Test"):
    for file_name in files:
        file_path = os.path.join(root, file_name)
        image = Image.open(file_path)
        resized_image = image.resize((224, 224))
        resized_image.save(file_path)

    batch_size = 32

    image_size = (150, 150)
    # Processamento da base de treino
    ds_train = tf.keras.preprocessing.image_dataset_from_directory(
        "fruits-360-original-size/Training/", labels='inferred', shuffle = True,
        color_mode='rgb', batch_size=batch_size, image_size=image_size, seed=1234,
        validation_split=0.2, subset="training")

    # Processamento da base de validação
    ds_test = tf.keras.preprocessing.image_dataset_from_directory(
        "fruits-360-original-size/Test/", labels='inferred', shuffle = True,
        color_mode='rgb', batch_size=batch_size, image_size=image_size, seed=1234,
        validation_split=0.2, subset="validation")

    # Processamento da base de validação
    ds_valid_test = tf.keras.preprocessing.image_dataset_from_directory(
        "fruits-360-original-size/Validation/", labels='inferred', shuffle = True,
        color_mode='rgb', batch_size=batch_size, image_size=image_size, seed=1234,
        validation_split=0.2, subset="validation")

    # Visualização
    plt.figure(figsize=(14, 8))
    for images, labels in ds_train.take(1):
        for i in range(16):
            ax = plt.subplot(4, 4, i + 1)
            plt.imshow(images[i].numpy().astype("uint8"))
            plt.title(f"{int(labels[i])} - {ds_test.class_names[labels[i]]}")
            plt.axis("off")

    model = VGG19(include_top=False,weights='imagenet', input_shape=(150, 150, 3))

    for layer in model.layers:
        layer.trainable = False
    last_output = model.output

    from tensorflow.keras import Model

    def transfer_learning(last_output, model):
        x = tf.keras.layers.Flatten()(last_output)
        x = tf.keras.layers.Dense(1024, activation='relu')(x)
        x = tf.keras.layers.Dropout(0.3)(x)
        x = tf.keras.layers.Dense(num_class, activation='softmax')(x)
        model = Model(inputs=model.input, outputs=x)
        return model

    model_2 = transfer_learning(last_output, model)

    data_augmentation = tf.keras.Sequential([
        tf.keras.layers.experimental.preprocessing.RandomRotation(0.2),
        tf.keras.layers.experimental.preprocessing.RandomFlip("horizontal")
    ])
    augmented_dataset = ds_train.map(lambda x, y: (data_augmentation(x, training=True), y))

    total_files = len(ds_train.file_paths) + len(ds_valid_test.file_paths)
    num_class = len(ds_train.class_names)
    print(f"classe numbers {num_class}")
    nr_batch_test = int( total_files / batch_size * 0.15)
    print(nr_batch_test)
    ds_test = ds_valid_test.take(nr_batch_test)
    ds_val = ds_valid_test.skip(nr_batch_test)
    print('Batches for testing ', ds_test.cardinality())
    print('Batches for validating ', ds_val.cardinality())

    model_2.compile(optimizer = tf.keras.optimizers.Adam(learning_rate=0.001),
                loss = 'sparse_categorical_crossentropy', metrics=['accuracy'])
    history_2 = model_2.fit(augmented_dataset, validation_data = ds_val,
                            epochs = 40, verbose=1)

    def plot_hist(hist):
    accuracy = hist.history['accuracy']
    val_accuracy = hist.history['val_accuracy']
    loss = hist.history['loss']
    val_loss = hist.history['val_loss']

    epochs = range(len(accuracy))

    plt.plot(epochs, accuracy, 'bo', label='Treinamento Accuracy')
    plt.plot(epochs, val_accuracy, 'b', label='Validação Accuracy')
    plt.title('Acurácia sobre treinamento x validação')
    plt.legend()

    score = model_2.evaluate(ds_test)
    print('Avaliação da acurácia : {:.4f}'.format(score[1]))

    from tqdm import tqdm
    y_true = []
    y_samples = []

    for x, labels in tqdm(ds_test):
    y_samples.append(x)
    y_true.append(labels.numpy())

    x_test = tf.concat([item for item in y_samples], axis = 0)
    y_test = tf.concat([item for item in y_true], axis = 0)

    print('Volume de fotos para teste ', len(y_test))

    y_pred_43response = model_2.predict(x_test)
    y_pred = np.argmax(y_pred_43response, axis=1)
    from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
    cmd=ConfusionMatrixDisplay(confusion_matrix(y_test, y_pred))
    cmd.plot()

    # Carregar o modelo VGG19 pré-treinado
    # model = VGG19(weights='imagenet')

    # Função para carregar e processar a imagem
    def load_and_process_image(image_path):
        img = load_img(image_path, target_size=(224, 224))
        img = img_to_array(img)
        img = np.expand_dims(img, axis=0)
        img = preprocess_input(img)
        return img

    # Função para prever a classe da imagem
    def predict_class(image_path):
        img = load_and_process_image(image_path)
        preds = model_2.predict(img)
        decoded_preds = decode_predictions(preds,  top=1)[0]
        return decoded_preds[0][1]

    predicted_class = predict_class(image_path)

    print("Classe predita:", predicted_class)

main()