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

	df = pd.read_csv('BTC_to_USD_CCCAGGedit.csv', sep=',', index_col=0) #delimiter to use and column to be used as row labels (ie time)
	#print(df.values) #prints dataframe values
	data = df.values
	data = data.astype('float32') #cast to specified type (for keras)

	# will probably want to use all attribs, but following tutorial which uses one (also not entirely sure how to correctly format the data for that, probably just need to remove column selection above)
	train = data[0:8000, :] #start at 0 and go to 8000 then stop, 3rd argument is step size
	test = data[8000:, :] #start at 8000 and finish, I think the comma is just a stopping point representation
	# gets all columns but the first due to index_col=0
	# print(train)
	# raw_input()
	# print(test)
	# raw_input()

	lags = 6
	X_train, y_train = prepare_data(train, lags)
	X_test, y_test = prepare_data(test, lags)
	y_true = y_test

	# print(X_train) #0th column (which is close since time was taken care of above)
	# raw_input()
	# print(y_train)

	plt.plot(y_test, label='OG data', color='#006699') #just to show that it is lagged by one, which it is (zoom in)
	plt.plot(X_test, label='OG data', color='orange')
	plt.legend(loc='upper left')
	plt.title('one period lagged')
	plt.show()

# #################### start of neural networks (which I am unknowledgeable about) ########################################## https://keras.io/
# 	mdl = Sequential() #simplest type of model (linear stack of layers). relu is an activation function of neural network
# 	mdl.add(Dense(3, input_dim=lags, activation='relu')) #.add adds layers to the model (the 3 is the output space, while input_dim gives input number, visual http://keras.dhpit.com/)
# 	mdl.add(Dense(1)) #next layer of size 1 (output layer)
# 	mdl.compile(loss='mean_squared_error', optimizer='adam') #configures model for training (mean squared error measures difference between estimator and what is estimated)
# 	# optimizer is some variant of stochastic gradient descent which tries to minimize an objective function (maps an event or values of vars onto a real number, cost)
# 	mdl.fit(X_train, y_train, epochs=200, batch_size=32, verbose=2) #iterate over trainig data in batches https://keras.io/models/model/
# ############## currently not looking right ####################### six titles for each for some reason (also 6 attribs)
# ############## editing data set to two variables made it look right (confused though since I thought the above only selected first column so I don't know how the other 5 came into play)
# ############## batch size is 32 by default. tutorial uses 2 which is significantly slower. Batch size defines number of samples that going to be propagated through the network.
# # https://stats.stackexchange.com/questions/153531/what-is-batch-size-in-neural-network very helpful in batch size explanation. boils down to accuracy

##################### next settings ##############################################################################################
	mdl = Sequential()
	mdl.add(Dense(6, input_dim=lags, activation='relu')) # 6
	mdl.add(Dense(12, activation='relu')) # another layer added. Each subsequent layer learns more complex representations # 12
	mdl.add(Dense(1)) # values from tutorial give a loss of 200000 as opposed to the random numbers I changed them to which give loss of about 9, I dont understand this crap
	mdl.compile(loss='mean_squared_error', optimizer='adam') # a lot of what i read says it's mostly fine tuning but im not sure why a difference of 2 and 4 would to lead to such an improvement
	mdl.fit(X_train, y_train, epochs=400, batch_size=2, verbose=2)


	train_score = mdl.evaluate(X_train, y_train, verbose=0)
	print('Train Score: {:.2f} MSE ({:.2f} RMSE)'.format(train_score, math.sqrt(train_score))) #formatting and crap
	train_score = mdl.evaluate(X_test, y_test, verbose=0)
	print('Train Score: {:.2f} MSE ({:.2f} RMSE)'.format(train_score, math.sqrt(train_score)))

##################### generate predictions for training #################################################
	train_predict = mdl.predict(X_train)
	test_predict = mdl.predict(X_test)

	# shift train predictions for plotting
	train_predict_plot = np.empty_like(data)
	train_predict_plot[:, :] = np.nan
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
	plt.title('Artificial Neural Network')
	plt.show()


if __name__ == "__main__":
	main()
