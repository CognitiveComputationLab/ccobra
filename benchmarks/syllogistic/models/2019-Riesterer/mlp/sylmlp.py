import time

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

import ccobra

import onehot

class SylMLP(nn.Module):
    def __init__(self):
        super(SylMLP, self).__init__()

        self.fc1 = nn.Linear(12, 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc3 = nn.Linear(256, 9)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

class MLPModel(ccobra.CCobraModel):
    def __init__(self, name='MLP-Adapt'):
        super(MLPModel, self).__init__(name, ['syllogistic'], ['single-choice'])

        # Initialize the neural network
        self.net = SylMLP()
        self.criterion = nn.MSELoss()
        self.optimizer = optim.Adam(self.net.parameters(), lr=1e-3)

        # General training properties
        self.n_epochs = 50
        self.n_epochs_adapt = 3
        self.batch_size = 8

    def pre_train(self, dataset, **kwargs):
        train_x = []
        train_y = []

        for subj_data in dataset:
            for task_data in subj_data:
                syllogism = ccobra.syllogistic.Syllogism(task_data['item'])

                # Encode the task input
                task = onehot.onehot_syllogism_content(syllogism.encoded_task)

                # Encode the response output
                encoded_response = syllogism.encode_response(task_data['response'])
                resp = onehot.onehot_response(encoded_response)

                train_x.append(task)
                train_y.append(resp)

        self.train_x = torch.from_numpy(np.array(train_x)).float()
        self.train_y = torch.from_numpy(np.array(train_y)).float()

        self.train_network(self.train_x, self.train_y, self.batch_size, self.n_epochs, verbose=True)

    def train_network(self, train_x, train_y, batch_size, n_epochs, verbose=False):
        for epoch in range(n_epochs):
            start_time = time.time()

            # Shuffle the training data
            perm_idxs = np.random.permutation(np.arange(len(train_x)))
            train_x = train_x[perm_idxs]
            train_y = train_y[perm_idxs]

            # Batched training loop
            losses = []
            for batch_idx in range(len(train_x) // batch_size):
                start = batch_idx * batch_size
                end = start + batch_size

                epoch_x = train_x[start:end]
                epoch_y = train_y[start:end]

                self.optimizer.zero_grad()

                # Optimize
                outputs = self.net(epoch_x)
                loss = self.criterion(outputs, epoch_y)
                loss.backward()
                self.optimizer.step()

                losses.append(loss.item())

            # Print statistics
            if verbose:
                print('Epoch {} ({:.2f}s): {}'.format(
                    epoch + 1, time.time() - start_time, np.mean(losses)))

    def person_train(self, data, **kwargs):
        pass

    def predict(self, item, **kwargs):
        # Encode the task
        syllogism = ccobra.syllogistic.Syllogism(item)

        # Query the model
        inp = onehot.onehot_syllogism_content(syllogism.encoded_task)
        inp_tensor = torch.from_numpy(inp).float()
        output = self.net(inp_tensor)

        # Return maximum response
        response = output.argmax().item()
        enc_response = ccobra.syllogistic.RESPONSES[response]
        return syllogism.decode_response(enc_response)

    def adapt(self, item, truth, **kwargs):
        syllogism = ccobra.syllogistic.Syllogism(item)

        # Onehot encoding
        onehot_syl = onehot.onehot_syllogism_content(syllogism.encoded_task)
        onehot_resp = onehot.onehot_response(syllogism.encode_response(truth))

        adapt_x = torch.from_numpy(onehot_syl.reshape(1, -1)).float()
        adapt_y = torch.from_numpy(onehot_resp.reshape(1, -1)).float()

        self.train_network(adapt_x, adapt_y, 1, self.n_epochs_adapt, verbose=False)
