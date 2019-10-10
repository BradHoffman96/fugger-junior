import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import ElasticNet
from sklearn.linear_model import Lasso
from sklearn.model_selection import train_test_split
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

### 1. Import, check & prepare
btc_to_usd = pd.read_csv(
    "/Users/shanekimble/Dropbox/fugger-junior/BTC_to_USD_CCCAGG.csv")  # Adjust

### 2. Partition
X = btc_to_usd.drop(columns='close')
y = btc_to_usd['close']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.4, random_state=0)

############################
### 1. Linear Regression ###
############################
# This is the model in action
lr_model = LinearRegression()
lr_model.fit(X_train, y_train)
lr_model.score(X_test, y_test)  # Coefficient of determination R^2
y_lr_predict = lr_model.predict(X_test)

# Keep in mind, this is plotting one feature, and is NOT the model in action
# The red dots are the RESULT of the model in action.
sns.set(rc={'figure.figsize': (50, 25)})
fig, ax = plt.subplots()
sns.regplot(
    X_test['time'], y_lr_predict, btc_to_usd, order=3, marker='+')  # Estimated
ax2 = ax.twinx()
sns.regplot(X_test['time'], y_test, btc_to_usd, order=3, color='red', marker='*')
plt.title('Linear Regression')
plt.xlabel("time")
plt.ylabel("close")
blue_line = mlines.Line2D(
    [], [], color='blue', marker='+', markersize=15, label='Predicted')
red_line = mlines.Line2D(
    [], [], color='red', markersize=15, marker='*', label='Actual')
plt.legend(handles=[blue_line, red_line])
plt.show()

######################
### 2. Elastic Net ###
######################
# This is the model in action
en_model = ElasticNet()
en_model.fit(X_train, y_train)
en_model.score(X_test, y_test)  # Coefficient of determination R^2
y_en_predict = en_model.predict(X_test)

# Keep in mind, this is plotting one feature, and is NOT the model in action
# The red dots are the RESULT of the model in action.
fig, ax = plt.subplots()
sns.regplot(
    X_test['time'], y_en_predict, btc_to_usd, ax=ax, order=3,
    truncate=True, marker='+')  # Estimated
ax2 = ax.twinx()
sns.regplot(
    X_test['time'],
    y_test,
    btc_to_usd,
    ax=ax2,
    color='r',
    truncate=True,
    order=3,
    marker='+')  # Actual
plt.title('Elastic Net Regression')
plt.xlabel("time")
plt.ylabel("close")
blue_line = mlines.Line2D(
    [], [], color='blue', marker='+', markersize=15, label='Predicted')
red_line = mlines.Line2D(
    [], [], color='red', markersize=15, marker='*', label='Actual')
plt.legend(handles=[blue_line, red_line])
plt.show()  # Predicted is red, actual is blue

################
### 3. Lasso ###
################
lasso_model = Lasso()
lasso_model.fit(X_train, y_train)
lasso_model.score(X_test, y_test)  # Coefficient of determination R^2
y_lasso_predict = en_model.predict(X_test)

# Keep in mind, this is plotting one feature, and is NOT the model in action
# The red dots are the RESULT of the model in action.
fig, ax = plt.subplots()
sns.regplot(
    X_test['time'], y_lasso_predict, btc_to_usd, ax=ax, order=3,
    truncate=True, marker='+')  # Estimated
ax2 = ax.twinx()
sns.regplot(
    X_test['time'],
    y_test,
    btc_to_usd,
    ax=ax2,
    color='r',
    truncate=True,
    order=3,
    marker='+')  # Actual
plt.title('Lasso Regression')
plt.xlabel("time")
plt.ylabel("close")
blue_line = mlines.Line2D(
    [], [], color='blue', marker='+', markersize=15, label='Predicted')
red_line = mlines.Line2D(
    [], [], color='red', markersize=15, marker='*', label='Actual')
plt.legend(handles=[blue_line, red_line])
plt.show()  # Predicted is red, actual is blue
