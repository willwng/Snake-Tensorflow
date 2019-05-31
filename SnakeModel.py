import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
import os
from ann_visualizer.visualize import ann_viz

old = np.load
np.load = lambda *a, **k: old(*a, allow_pickle=True, **k)
os.environ["PATH"] += os.pathsep + r'C:\Program Files (x86)\Graphviz2.38\bin'

file_name = str(input("Enter Training Data Name: ")) + '.npy'
print("Read File from: ", file_name)
epochs = int(input("Number of Epochs? "))

def build_model(input_size, output_size):
    print(input_size)
    model = Sequential()
    model.add(Dense(12, input_dim=input_size, activation='relu'))
    model.add(Dense(output_size, activation='linear'))
    model.compile(loss='mse', optimizer=Adam())

    return model


def train_model(training_data, epochs):
    inp = np.array([i[0] for i in training_data]).reshape(-1, len(training_data[0][0]))
    target = np.array([i[1] for i in training_data]).reshape(-1, len(training_data[0][1]))
    model = build_model(input_size=len(inp[0]), output_size=len(target[0]))

    model.fit(inp, target, epochs=epochs)
    return model


train_data = np.load(file_name)
train_data = np.asarray(train_data)
# print(train_data)
fit_model = train_model(train_data, epochs)
# ann_viz(fit_model)
fit_model.save('FittedModel.model')
