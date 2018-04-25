# primary tutorial used http://dacatay.com/data-science/part-6-time-series-prediction-neural-networks-python/ much more googling and other links used for understanding
import sys
import pandas as pd
import math
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt

def prepare_data(data, lags):
	X, y = [], [] # this comma stuff is numpy exclusive
	for row in range(len(data) - lags -1): #for every index except for last one
		a = data[row:(row + lags), 0] #, used to specify column number (0) for column zero it is going from row to row + offset of data and storing it in a
		X.append(a) #appends slice to x so n and to n+1 or n to n+lags
		y.append(data[row + lags, 0]) #appends n+lags to data
	return np.array(X), np.array(y) #returns the arrays


def main(lags):
	lags = int(lags)
	np.random.seed(7)
	df = pd.read_csv('BTC_to_USD_CCCAGGedit.csv', sep=',', parse_dates=True, index_col=0) #delimiter to use and column to be used as row labels (ie time)
	data = df.values
	data = data.astype('float32') #cast to specified type (for keras)

	train = data[0:8000, :] #start at 0 and go to 8000 then stop, 3rd argument is step size
	test = data[8000:, :] #start at 8000 and finish, I think the comma is just a stopping point representation

	X_train, y_train = prepare_data(train, lags)
	X_test, y_test = prepare_data(test, lags)
	y_true = y_test

	# plt.plot(y_test, label='OG data', color='#006699') #just to show that it is lagged by one, which it is (zoom in)
	# plt.plot(X_test, label='OG data', color='orange')
	# plt.legend(loc='upper left')
	# plt.title('%d period lagged' % lags)
	# plt.show()

	mdl = Sequential()
	mdl.add(Dense(12, input_dim=lags, activation='relu'))
	mdl.add(Dense(8, activation='relu'))
	# mdl.add(Dense(36, activation='relu')) #these make test mse worse
	# mdl.add(Dense(8, activation='relu')) #lower the mse the better the model
	mdl.add(Dense(1))
	mdl.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])
	hist = mdl.fit(X_train, y_train, validation_split=0.66, epochs=100, batch_size=10, verbose=2) # more epochs lead to higher mse

	train_score = mdl.evaluate(X_train, y_train, verbose=0)
	print('Train Score: {:.2f} MSE ({:.2f} RMSE)'.format(float(train_score[0]), math.sqrt(float(train_score[0])))) #formatting and crap
	test_score = mdl.evaluate(X_test, y_test, verbose=0)
	print('Test Score: {:.2f} MSE ({:.2f} RMSE)'.format(float(test_score[0]), math.sqrt(float(test_score[0]))))

##################### generate predictions for training #################################################
	train_predict = mdl.predict(X_train)
	test_predict = mdl.predict(X_test)

	# shift train predictions for plotting
	train_predict_plot = np.empty_like(data)
	train_predict_plot[:, :] = np.nan #Return a new array with the same shape and type as a given array.
	train_predict_plot[lags: len(train_predict) + lags, :] = train_predict

	# shift test predictions for plotting
	test_predict_plot = np.empty_like(data)
	test_predict_plot[:, :] = np.nan
	test_predict_plot[len(train_predict)+(lags*2)+1:len(data)-1, :] = test_predict

	# plot baseline and predictions
	plt.plot(data, label='Observed', color='#006699'); #duplicating labels for some reason
	plt.plot(train_predict_plot, label='Prediction for Train Set', color='#006699', alpha=0.5);
	plt.plot(test_predict_plot, label='Prediction for Test Set', color='#ff0066');
	plt.legend(loc='best');
	plt.xlabel('time (data row)')
	plt.ylabel('Close')
	plt.title('Artificial Neural Network')
	plt.show()

	meme1 = hist.history['loss'].pop(0) #first value can be exceptionally higher so makes graph look weird
	meme2 = hist.history['val_loss'].pop(0)

	plt.plot(hist.history['loss']) # https://machinelearningmastery.com/display-deep-learning-model-training-history-in-keras/
	plt.plot(hist.history['val_loss'])
	plt.title('model loss')
	plt.ylabel('loss')
	plt.xlabel('epoch')
	plt.legend(['train', 'test'], loc='upper left')
	plt.show()

	# plt.plot(hist.history['acc']) # this is a mess
	# plt.plot(hist.history['val_acc'])
	# plt.title('model accuracy')
	# plt.ylabel('accuracy')
	# plt.xlabel('epoch')
	# plt.legend(['train', 'test'], loc='upper left')
	# plt.show()


if __name__ == "__main__":
	main(sys.argv[1])
