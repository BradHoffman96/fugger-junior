# primary tutorial used http://dacatay.com/data-science/part-6-time-series-prediction-neural-networks-python/ much more googling and other links used for understanding
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


def main():
	np.random.seed(7)
	df = pd.read_csv('BTC_to_USD_CCCAGGedit.csv', sep=',', parse_dates=True, index_col=0) #delimiter to use and column to be used as row labels (ie time)
	data = df.values
	data = data.astype('float32') #cast to specified type (for keras)

	train = data[0:8000, :] #start at 0 and go to 8000 then stop, 3rd argument is step size
	test = data[8000:, :] #start at 8000 and finish, I think the comma is just a stopping point representation

	lags = 8
	X_train, y_train = prepare_data(train, lags)
	X_test, y_test = prepare_data(test, lags)
	y_true = y_test

	# plt.plot(y_test, label='OG data', color='#006699') #just to show that it is lagged by one, which it is (zoom in)
	# plt.plot(X_test, label='OG data', color='orange')
	# plt.legend(loc='upper left')
	# plt.title('one period lagged')
	# plt.show()

	mdl = Sequential()
	mdl.add(Dense(12, input_dim=lags, activation='relu')) # 6 https://keras.io/initializers/ might need to add initial random weights to keras layers
	mdl.add(Dense(24, activation='relu')) # another layer added. Each subsequent layer learns more complex representations # 12
	mdl.add(Dense(1)) # values from tutorial give a loss of 200000 as opposed to the random numbers I changed them to which give loss of about 9, I dont understand this crap
	mdl.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy']) # a lot of what i read says it's mostly fine tuning but im not sure why a difference of 2 and 4 would to lead to such an improvement
	hist = mdl.fit(X_train, y_train, validation_split=0.66, epochs=400, batch_size=10, verbose=2) #returns a history object so should be able to isolate data from each epoch
	# https://www.quora.com/What-is-the-importance-of-the-validation-split-variable-in-Keras for a n explanation on validation split, not sure what is the best value, but gives more metrics
	# print hist.history.keys()
	# print hist.history['loss'] # these are for each epoch
	# print hist.history['acc']
	# validation split changes the results of the loss from verbose 2 ^ but graph is same (not sure about this?)

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

	plt.plot(hist.history['loss']) # https://machinelearningmastery.com/display-deep-learning-model-training-history-in-keras/
	plt.plot(hist.history['val_loss']) # trying to determine how well the model is going, but a drastic improvement in the first couple generations seems to make this useless
	plt.title('model loss')
	plt.ylabel('loss')
	plt.xlabel('epoch')
	plt.legend(['train', 'test'], loc='upper left')
	plt.show()


if __name__ == "__main__":
	main()
