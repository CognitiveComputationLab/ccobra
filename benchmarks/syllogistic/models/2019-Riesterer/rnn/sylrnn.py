import time

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

import ccobra

import onehot

class RNN(nn.Module):
    def __init__(self, input_size=12, hidden_size=64, output_size=9):
        super(RNN, self).__init__()

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=2,
            dropout=0.2)
        self.h2o = nn.Linear(hidden_size, 9)

    def forward(self, input, hidden):
        output, hidden = self.lstm(input, hidden)
        output = self.h2o(output)
        return output, hidden

class RNNModel(ccobra.CCobraModel):
    def __init__(self, name='RNN'):
        super(RNNModel, self).__init__(
            name, ['syllogistic'], ['single-choice'])

        self.net = RNN()
        self.hidden = None

        # Training parameters
        self.n_epochs = 13

        # Training algorithms
        self.optimizer = optim.Adam(self.net.parameters())
        self.criterion = nn.CrossEntropyLoss()

    def pre_train(self, dataset):
        # Prepare the data for training by converting it into a 64 x n_subj x 12
        train_x = []
        train_y = []

        for subj_data in dataset:
            subj_train_x = []
            subj_train_y = []

            for task_data in subj_data:
                syllogism = ccobra.syllogistic.Syllogism(task_data['item'])

                # Onehot encodings
                onehot_task = onehot.onehot_syllogism_content(syllogism.encoded_task)
                onehot_response = onehot.onehot_response(
                    syllogism.encode_response(task_data['response']))

                subj_train_x.append(onehot_task)
                subj_train_y.append(onehot_response)

            train_x.append(subj_train_x)
            train_y.append(subj_train_y)

        self.train_x = torch.from_numpy(np.array(train_x)).float()
        self.train_y = torch.from_numpy(np.array(train_y)).float()

        self.train_network(self.train_x, self.train_y, self.n_epochs, verbose=True)

    def train_network(self, train_x, train_y, n_epochs, verbose=False):
        print('Starting training...')
        for epoch in range(self.n_epochs):
            start_time = time.time()

            # Shuffle the training data
            perm_idxs = np.random.permutation(np.arange(len(train_x)))
            train_x = train_x[perm_idxs]
            train_y = train_y[perm_idxs]

            # Loop over the training instances
            losses = []
            for idx in range(len(train_x)):
                cur_x = train_x[idx]
                cur_y = train_y[idx]

                input = cur_x.view(64, 1, -1)
                outputs, _ = self.net(input, None)

                # Backpropagation and parameter optimization
                loss = self.criterion(outputs.view(64, -1), cur_y.argmax(1))
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

                losses.append(loss.item())

            # Print statistics
            print('Epoch {}/{} ({:.2f}s): {:.4f} ({:.4f})'.format(
                epoch + 1, n_epochs, time.time() - start_time, np.mean(losses), np.std(losses)))

            # Test the predictive accuracy
            accs = []
            for subj_idx in range(len(self.train_x)):
                pred, _ = self.net(self.train_x[subj_idx].view(64, 1, -1), None)
                pred_max = pred.view(64, -1).argmax(1)
                truth = self.train_y[subj_idx].argmax(1)

                acc = torch.mean((pred_max == truth).float()).item()
                accs.append(acc)

            print('   acc mean: {:.2f}'.format(np.mean(accs)))
            print('   acc std : {:.2f}'.format(np.std(accs)))

            # input = torch.from_numpy(onehot.onehot_syllogism_content('AA1')).float().view(1, -1)
            # print('   AA1:', self.net(input, self.net.initHidden()))

            self.net.eval()

    def predict(self, item, **kwargs):
        syllogism = ccobra.syllogistic.Syllogism(item)

        # Obtain the prediction
        input = torch.from_numpy(onehot.onehot_syllogism_content(syllogism.encoded_task)).float()
        output, self.hidden = self.net(input.view(1, 1, -1), self.hidden)

        # Return maximum response
        response = output.argmax().item()
        enc_response = ccobra.syllogistic.RESPONSES[response]
        return syllogism.decode_response(enc_response)
