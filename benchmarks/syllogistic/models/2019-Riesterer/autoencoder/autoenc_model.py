import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import ccobra

import autoencoder

class SylMLPModel(ccobra.CCobraModel):
    def __init__(self, name='Autoencoder'):
        super(SylMLPModel, self).__init__(name, ['syllogistic'], ['single-choice'])

        self.net = autoencoder.DenoisingAutoencoder()
        print('n_parameters:', len(list(self.net.parameters())))
        print(self.net)

        self.optimizer = optim.Adam(self.net.parameters())
        self.criterion = nn.MSELoss()

        self.history = torch.zeros((576,))

    def pre_train(self, dataset):
        # Extract the training data and result targets from the training dataset
        train_x = []
        train_y = []
        for train_subject in dataset:
            user_vector = np.zeros((576,), dtype='int')

            for train_task in train_subject:
                syllogism = ccobra.syllogistic.Syllogism(train_task['item'])

                enc_task = syllogism.encoded_task
                enc_truth = syllogism.encode_response(train_task['response'])

                task_idx = ccobra.syllogistic.SYLLOGISMS.index(enc_task)
                truth_idx = ccobra.syllogistic.RESPONSES.index(enc_truth)

                user_vector[task_idx * 9 + truth_idx] = 1

            train_x.append(user_vector)
            train_y.append(user_vector)

        train_x = torch.from_numpy(np.array(train_x)).float()
        train_y = torch.from_numpy(np.array(train_y)).float()

        print('train_x:', train_x.shape)
        print('train_y:', train_y.shape)

        batch_size = 32
        epochs = 30
        for epoch in range(epochs):
            # Randomize the inputs
            permutation = np.random.permutation(np.arange(len(train_x)))
            train_x = train_x[permutation]
            train_y = train_y[permutation]

            epoch_losses = []
            for mb_idx in range(len(train_x) // batch_size):
                start = mb_idx * batch_size
                end = start + batch_size

                mb_x = train_x[start:end]
                mb_y = mb_x

                # Noise the input
                input_data = mb_x
                noise = torch.bernoulli(torch.zeros_like(input_data) + 0.8)
                input_data = input_data * noise

                # Perform the training on the minibatch
                self.optimizer.zero_grad()

                outputs = self.net(input_data)
                loss = self.criterion(outputs, mb_y)
                loss.backward()
                self.optimizer.step()

                epoch_losses.append(loss.item())

            print('Epoch {}/{}: {}...'.format(epoch + 1, epochs, np.mean(epoch_losses)))

    def predict(self, item, **kwargs):
        syllogism = ccobra.syllogistic.Syllogism(item)
        enc_task = syllogism.encoded_task
        task_idx = ccobra.syllogistic.SYLLOGISMS.index(enc_task)

        # Query the network for the user completion
        pred_idx = self.net(self.history)[task_idx*9:task_idx*9+9].argmax().item()
        return syllogism.decode_response(ccobra.syllogistic.RESPONSES[pred_idx])

    def adapt(self, item, truth, **kwargs):
        syllogism = ccobra.syllogistic.Syllogism(item)
        syl_idx = ccobra.syllogistic.SYLLOGISMS.index(syllogism.encoded_task)
        truth_idx = ccobra.syllogistic.RESPONSES.index(syllogism.encode_response(truth))
        self.history[syl_idx * 9 + truth_idx] = 1
