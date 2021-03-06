# -*- coding: utf-8 -*-
"""Classification_final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PUaGre38SYpb5uEILiiGzdonVvSV-C6Y
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import datetime as dt
import re
import pickle 
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import pandas_profiling
import pydotplus
# %matplotlib inline

# Data and Numbers
import pandas as pd
import numpy as np
import datetime as dt

# Modeling
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.metrics import precision_score, recall_score,\
precision_recall_curve,f1_score, fbeta_score,\
accuracy_score, confusion_matrix, roc_auc_score, roc_curve
from sklearn.naive_bayes import BernoulliNB, GaussianNB
from xgboost import XGBClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import BaggingClassifier, RandomForestClassifier
from sklearn import svm
from sklearn.svm import LinearSVC, SVC
from sklearn.preprocessing import StandardScaler
from sklearn.externals.six import StringIO


# Saving
import joblib
import pickle

# Plotting
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import Image

from sklearn.tree import export_graphviz
# %matplotlib inline
from matplotlib import rcParams
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Oswald']
font = {'size'   : 12}
plt.rc('font', **font)

# %precision 5

startdataclass = pd.read_csv('/content/sample_data/CleanedData.csv')



startdataclass

startdataclass.shape

startdataclass.info()

startdataclass['val_AnnualGrowthRate(%)']= startdataclass['val_AnnualGrowthRate(%)'].astype(float)
startdataclass['val_AbsoluteGrowthRate(%)'] = startdataclass['val_AbsoluteGrowthRate(%)'].astype(float)

startdataclass.info()

startdataclass['val_FTcategory'] = startdataclass.val_FTcategory.apply(str.split,sep='|')

# Create list of category lists
categories = list(startdataclass.val_FTcategory)
# Flatten the list
flat_categories = [cat for sublist in categories for cat in sublist]
# Count occurences of each
category_counts = Counter(flat_categories).most_common()
# Look at the distribution
plt.figure(figsize=(9, 5))
plt.bar([x[0] for x in category_counts[0:50]],
        [x[1] for x in category_counts[0:50]],
        width=0.8)
plt.xticks(rotation=90)
plt.title('50 Most Commonly Occuring Categories')
sns.despine()

# Take the top 25
top_cats = [x[0] for x in category_counts[0:25]]

#For each company with a category listed in the top 25 categories, replace its cat_list with that single category

startdataclass.val_FTcategory = startdataclass.val_FTcategory.map(
    lambda x: list(set(x) & set(top_cats))
    if set(x) & set(top_cats) else ['0_other_cat'])

# Create list of category lists
categories = list(startdataclass.val_FTcategory)
# Flatten the list
flat_categories = [cat for sublist in categories for cat in sublist]
# Count occurences of each
category_counts = Counter(flat_categories).most_common()
# Look at the distribution
plt.figure(figsize=(9, 5))
plt.bar([x[0] for x in category_counts[0:25]],
        [x[1] for x in category_counts[0:25]],
        width=0.8)
plt.xticks(rotation=90)
sns.despine()
plt.title('Top Categories')

# This will be used to create dummy variables in the feature matrix
startdataclass.val_FTcategory = startdataclass.val_FTcategory.apply(
    lambda x: x[0])

# Country
# Fill empty country with 'unknown'
startdataclass.val_Country .fillna('unknown', inplace=True)

# Look at distribution
country_dist = startdataclass.groupby(
    'val_Country').size().sort_values(ascending=False)
plt.bar(country_dist[0:10].index, height=country_dist[0:10].values)
plt.xticks(rotation=90)
sns.despine()
plt.title('Distribution of Top 10 Countries')

startdataclass.columns



# Category Dummies
cat_dummies = pd.get_dummies(startdataclass['val_FTcategory'], drop_first=True)
# Country Dummies
country_dummies = pd.get_dummies(startdataclass['val_Country'], drop_first=True)
val_AbsoluteGrowthRate_dummies = pd.get_dummies(startdataclass['val_AbsoluteGrowthRate(%)'], drop_first=True)
val_AnnualGrowthRate_dummies = pd.get_dummies(startdataclass['val_AnnualGrowthRate(%)'], drop_first=True)

# Create dummy variables for category, country, and state

X_col_nodummies = [
     'val_AnnualGrowthRate(%)',
    'val_AbsoluteGrowthRate(%)'
]
X_nodummies = startdataclass[X_col_nodummies]

# Merge in dummies to feature matrix
X = X_nodummies.merge(cat_dummies, left_index=True, right_index=True).merge(
    country_dummies, left_index=True, right_index=True)

# Add intercept column
X['intercept'] = 1

# Create binary status column where 0 = closed, 1 = aqcquired/IPO
startdataclass['Rank_bool'] = np.nan

# Fill the column
startdataclass.loc[np.logical_or(
    startdataclass.val_2019Rank == 'yes', startdataclass.
    val_2019Rank == 'yes'), 'Rank_bool'] = 0
startdataclass.loc[np.logical_or(
    startdataclass.val_2019Rank == 'no', startdataclass.Rank_bool
    == 'no'), 'Rank_bool'] = 1

startdataclass.Rank_bool.value_counts()

y = startdataclass.Rank_bool

sns.pairplot(startdataclass[X_col_nodummies + ['Rank_bool']], hue='Rank_bool')

# Count target values
target_count = y.value_counts()

# # print class balance
print(f'Class 0: {target_count[0]}')
print(f'Class 1: {target_count[1]}')
print(f'Proportion: {round(target_count[0] / target_count[1], 2)} : 1')
print('Percentage of Majority Class: {:f}'.format(
    round(target_count[0] / sum(target_count), 4) * 100))

target_count

# Split the data with 80% to train and 20% to test
# Stratify to ensure train and test sets have 
# similar proportions of either target class
X_train, X_test, y_train, y_test = train_test_split(X,
                                                    y,
                                                    test_size=0.2,
                                                    random_state=40,
                                                    stratify=y)

# Standardize the data

scaler = StandardScaler()

# Fit the scaler using the training data and scale it
X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train.values),
                              columns=X.columns)

# Scale the test data
X_test_scaled = pd.DataFrame(scaler.transform(X_test.values),
                             columns=X.columns)

# Instantiate model
logreg = LogisticRegression(C=10, solver='lbfgs')

# Fit model to the training data
logreg.fit(X_train_scaled, y_train)
# Pickle this for later
joblib.dump(logreg, 'logreg.pkl')

# Calculate ROC curve for logistic regression
fpr_lr, tpr_lr, thresholds_lr = roc_curve(
    y_test,
    logreg.predict_proba(X_test_scaled)[:, 1])

# Calculate area under the curve (AUC) for ROC
auc_lr = roc_auc_score(y_test, logreg.predict_proba(X_test_scaled)[:, 1])

def fbeta(model, y_test=y_test, X_test=X_test_scaled):
    """
    Calculate the probability threshold that yields the highest f_beta value
    input: fitted model, y_test, X_test
    """
    prob_thresholds = np.arange(0, 1, 0.005)
    fbeta = []
    for prob in prob_thresholds:
        fbeta.append(
            fbeta_score(y_test,
                        model.predict_proba(X_test)[:, 1] > prob, 3))
    all_fbeta = list(zip(prob_thresholds, fbeta))
    best_fbeta = max(list(zip(prob_thresholds, fbeta)), key=lambda x: x[1])
    print(
        'Probability that yields the best fbeta score is {} with fbeta={:5f}'.
        format(best_fbeta[0], best_fbeta[1]))
    return all_fbeta, best_fbeta

# Calculate fbeta for logistic regression
all_fbeta_lr, best_fbeta_lr = fbeta(logreg, X_test=X_test_scaled)
p_thresh = best_fbeta_lr[0]

precision_curve, recall_curve, threshold_curve = precision_recall_curve(
    y_test,
    logreg.predict_proba(X_test_scaled)[:, 1])

plt.figure(dpi=80)
plt.plot(threshold_curve, precision_curve[1:], label='precision')
plt.plot(threshold_curve, recall_curve[1:], label='recall')
plt.plot(list(zip(*all_fbeta_lr))[0],
         list(zip(*all_fbeta_lr))[1],
         label='fbeta')
plt.plot([best_fbeta_lr[0], best_fbeta_lr[0]], [-1, best_fbeta_lr[1]],
         '--',
         color='black',
         alpha=0.5)
plt.plot(best_fbeta_lr[0], best_fbeta_lr[1], 'o')
plt.ylim([-0.1, 1.1])
plt.legend(loc='lower left')
plt.xlabel('Threshold (above this probability, label as success)')
plt.title('LogReg Precision, Recall, and fbeta Curves')
sns.despine()

lr_coefs = list(zip(X.columns, logreg.coef_[0]))
lr_coefs_df = pd.DataFrame(lr_coefs)
lr_top_coefs = [x for x in lr_coefs if np.abs(x[1]) > .07]
lr_top_coefs = sorted(lr_top_coefs, key=(lambda x: x[1]), reverse=True)
lr_top_coefs_df = pd.DataFrame(lr_top_coefs)

plt.barh([x[0] for x in lr_top_coefs], width=[x[1] for x in lr_top_coefs])
plt.title('LogOdds')
plt.grid(b=False)
sns.despine()

dt = DecisionTreeClassifier(max_depth=5)
dt.fit(X_train, y_train)

# Calculate fbeta for decision tree
all_fbeta_dt, best_fbeta_dt = fbeta(dt,
                                    X_test=X_test)  # not scaled data for dt

# Calculate ROC Score and AUC for decision tree
fpr_dt, tpr_dt, thresholds_dt = roc_curve(
    y_test,
    dt.predict_proba(X_test)[:, 1])  # not scaled data for dt
auc_dt = roc_auc_score(y_test, dt.predict_proba(X_test)[:, 1])

# This allows us to make a decision tree real fast directly in the notebook!
dot_data = StringIO()
export_graphviz(dt,
                out_file=dot_data,
                feature_names=X_train.columns.tolist(),
                filled=True,
                rounded=True,
                special_characters=True)
graph = pydotplus.graph_from_dot_data(dot_data.getvalue())

# Feature importance

pd.DataFrame({
    'feature': X.columns,
    'importance': dt.feature_importances_
}).sort_values(by='importance', ascending=False)[0:15]

# Instantiate Model
knn = KNeighborsClassifier(n_neighbors=5)

# Fit Model
knn.fit(X_train_scaled, y_train)

# Calculate fbeta for KNN
all_fbeta_knn, best_fbeta_knn = fbeta(knn,
                                      X_test=X_test_scaled)  # scaled for knn

# Calculate ROC Score and AUC for knn
fpr_knn, tpr_knn, thresholds_knn = roc_curve(
    y_test,
    knn.predict_proba(X_test_scaled)[:, 1])  # scaled for knn
auc_knn = roc_auc_score(
    y_test,
    knn.predict_proba(X_test_scaled)[:, 1])  # scaled for knn

nbb = BernoulliNB()
nbb.fit(X_train_scaled, y_train)

# Calculate fbeta for Naive Bayes Bernoulli
all_fbeta_nbb, best_fbeta_nbb = fbeta(nbb,
                                      X_test=X_test_scaled)  # scaled for nbb

# Calculate ROC Score and AUC for Naive Bayes Bernoulli
fpr_nbb, tpr_nbb, thresholds_nbb = roc_curve(
    y_test,
    nbb.predict_proba(X_test_scaled)[:, 1])  # scaled for nbb
auc_nbb = roc_auc_score(
    y_test,
    nbb.predict_proba(X_test_scaled)[:, 1])  # scaled for nbb

nbg = GaussianNB()
nbg.fit(X_train_scaled, y_train)

# Calculate fbeta for Naive Bayes Gaussian
all_fbeta_nbg, best_fbeta_nbg = fbeta(nbg,
                                      X_test=X_test_scaled)  # scaled for nbg

# Calculate ROC Score and AUC for Naive Bayes Gaussian
fpr_nbg, tpr_nbg, thresholds_nbg = roc_curve(
    y_test,
    nbg.predict_proba(X_test_scaled)[:, 1])  # scaled for nbg
auc_nbg = roc_auc_score(
    y_test,
    nbg.predict_proba(X_test_scaled)[:, 1])  # scaled for nbg

svm_model = svm.SVC(kernel="linear", probability=True)
svm_model.fit(X_train_scaled, y_train)

# Calculate fbeta for SVM
all_fbeta_svm_model, best_fbeta_svm_model = fbeta(
    svm_model, X_test=X_test_scaled)  # scaled for SVM

# Calculate ROC Score and AUC for SVM
fpr_svm_model, tpr_svm_model, thresholds_svm_model = roc_curve(
    y_test,
    svm_model.predict_proba(X_test_scaled)[:, 1])  # scaled for SVM
auc_svm_model = roc_auc_score(
    y_test,
    svm_model.predict_proba(X_test_scaled)[:, 1])  # scaled for SVM

xgb = XGBClassifier()
xgb.fit(X_train, y_train)

# Calculate fbeta for XGBoost
prob_thresholds = np.arange(0, 1, 0.005)
fbeta_xgb = []
for prob in prob_thresholds:
    fbeta_xgb.append(
        fbeta_score(y_test,
                    xgb.predict_proba(X_test)[:, 1] > prob, 3))
all_fbeta_xgb = list(zip(prob_thresholds, fbeta_xgb))
best_fbeta_xgb = max(list(zip(prob_thresholds, fbeta_xgb)), key=lambda x: x[1])
print('Probability that yields the best fbeta score is {} with fbeta={:5f}'.
      format(best_fbeta_xgb[0], best_fbeta_xgb[1]))

# Calculate ROC Score and AUC for Naive Bayes Gaussian
fpr_xgb, tpr_xgb, thresholds_xgb = roc_curve(
    y_test,
    xgb.predict_proba(X_test)[:, 1])  # not scaled for xgboost
auc_xgb = roc_auc_score(
    y_test,
    xgb.predict_proba(X_test)[:, 1])  # not scaled for xgboost

bag_dt = BaggingClassifier(DecisionTreeClassifier(),
                           n_estimators=500,
                           bootstrap=True,
                           oob_score=True,
                           random_state=1234,
                           n_jobs=-1)
# fit
bag_dt.fit(X_train, y_train)

# Calculate fbeta for Bagging Decision Trees
all_fbeta_bag_dt, best_fbeta_bag_dt = fbeta(
    bag_dt, X_test=X_test)  # not scaled for bag_dt

# Calculate ROC Score and AUC for bag dt
fpr_bag_dt, tpr_bag_dt, thresholds_bag_dt = roc_curve(
    y_test,
    bag_dt.predict_proba(X_test)[:, 1])  # not scaled for bag dt
auc_bag_dt = roc_auc_score(
    y_test,
    bag_dt.predict_proba(X_test)[:, 1])  # not scaled for bag dt

# Instantiate Model
rf = RandomForestClassifier(n_estimators=500,
                            bootstrap=True,
                            oob_score=True,
                            random_state=1234,
                            n_jobs=-1)

# fit
rf.fit(X_train, y_train)

# Calculate fbeta for Random Forest
all_fbeta_rf, best_fbeta_rf = fbeta(rf, X_test=X_test)  # not scaled for rf

# Calculate ROC Score and AUC for random forest
fpr_rf, tpr_rf, thresholds_rf = roc_curve(
    y_test,
    rf.predict_proba(X_test)[:, 1])  # not scaled for rf
auc_rf = roc_auc_score(y_test,
                       rf.predict_proba(X_test)[:, 1])  # not scaled for rf

# Feature importance

rf_feats = pd.DataFrame({
    'feature': X.columns,
    'importance': rf.feature_importances_
}).sort_values(by='importance', ascending=False)

# Look at top 10 features
rf_feats[0:10]

models = ['lr', 'dt', 'knn', 'nbb', 'nbg', 'svm', 'xgb', 'bag_dt', 'rf']
model_aucs = [
    auc_lr, auc_dt, auc_knn, auc_nbb, auc_nbg, auc_svm_model, auc_xgb,
    auc_bag_dt, auc_rf
]
model_fbetas = [
    best_fbeta_lr[1], best_fbeta_dt[1], best_fbeta_knn[1], best_fbeta_nbb[1],
    best_fbeta_nbg[1], best_fbeta_svm_model[1], best_fbeta_xgb[1],
    best_fbeta_bag_dt[1], best_fbeta_rf[1]
]
model_names = [
    'Logistic Regression', 'Decision Tree', 'KNN', 'Bernoulli Naive Bayes',
    'Gaussian Naive Bayes', 'Support Vector Machine', 'XGBoost',
    'Bagged Decision Tree', 'Random Forest'
]

# Plot ROC Curves

plt.plot(fpr_lr, tpr_lr, lw=1, label='Logistic Regression')
plt.plot(fpr_dt, tpr_dt, lw=1, label='Decision Tree')
plt.plot(fpr_knn, tpr_knn, lw=1, label='KNN')
plt.plot(fpr_nbb, tpr_nbb, lw=1, label='Bernoulli NB')
plt.plot(fpr_nbg, tpr_nbg, lw=1, label='Gaussian NB')
plt.plot(fpr_svm_model, tpr_svm_model, lw=1, label='SVM - Linear')
plt.plot(fpr_xgb, tpr_xgb, lw=1, label='XGBoost')
plt.plot(fpr_bag_dt, tpr_bag_dt, lw=1, label='Bagged DT')
plt.plot(fpr_rf, tpr_rf, lw=1, label='Random Forest')

plt.plot([0, 1], [0, 1], c='violet', ls='--')
plt.xlim([-0.05, 1.05])
plt.ylim([-0.05, 1.05])

plt.xlabel('False positive rate')
plt.ylabel('True positive rate')
plt.title('Model Comparison - ROC curve')
plt.legend(ncol=2, fontsize='small')
sns.despine()

# Print AUC Scores
for model in list(zip(model_names, model_aucs)):
    print("ROC AUC score = {:3f} for {}".format(model[1], model[0]))

# Print fbeta Scores
for model in list(zip(model_names, model_fbetas)):
    print("f_beta score = {:3f} for {}".format(model[1], model[0]))

lr_reg = LogisticRegression(solver='saga',
                            C=0.1,
                            penalty='elasticnet',
                            l1_ratio=0.95)
lr_reg.fit(X_train_scaled, y_train)



# Look at coefficients
lr_reg_coefs = pd.DataFrame(sorted(list(zip(X.columns, lr_reg.coef_[0])),
                                   key=(lambda x: x[1]),
                                   reverse=True),
                            columns=['Feature', 'Coefficient'])
lr_reg_coefs

# Only select features with strong coefficients
X_sel_cols = list(lr_reg_coefs[abs(lr_reg_coefs['Coefficient']) > 0.05]
                  ['Feature'])  # Only keep features with higher coefficients
X_sel_cols.append('val_AnnualGrowthRate(%)')
X_sel_cols.append('Norway')
X_sel_cols.append('Latvia')
X_sel_cols.append('Hungary')

X_sel_cols

# Save column names
joblib.dump(X_sel_cols, 'X_sel_cols.pkl')

X_sel_cols_reorder = [
    'val_AnnualGrowthRate(%)', 'Energy', 'Management Consulting',
    'Norway', 'Latvia', 'Sales & Marketing', 'Advertising',
    'Germany', 'Support Services', 'Italy','France',
    'val_AnnualGrowthRate(%)','Norway','Latvia','Hungary',
]

X_sel = X[X_sel_cols_reorder]

# Split the data with 80% to train and 20% to test
# Stratify to ensure train and test sets have 
# similar proportions of either target class
X_sel_train, X_sel_test, y_sel_train, y_sel_test = train_test_split(
    X_sel, y, test_size=0.2, random_state=40, stratify=y)

# Standardize the data with new scaler for selected columns

scaler_sel = StandardScaler()
scaler_sel.fit(X_sel_train.values)
# Save scaler for later
joblib.dump(scaler_sel,'scaler_sel.pkl')
with open("/content/sample_data/scaler_sel.pkl", "wb") as f:
    pickle.dump(scaler_sel, f)

# Fit the scaler using the training data and scale it
X_sel_train_scaled = pd.DataFrame(scaler_sel.transform(X_sel_train.values),
                                  columns=X_sel_cols_reorder)

# Scale the test data
X_sel_test_scaled = pd.DataFrame(scaler_sel.transform(X_sel_test.values),
                                 columns=X_sel_cols_reorder)

X_sel.columns

scaler_sel.transform(np.array(list(X_sel_test.iloc[1].values)).reshape(1, -1))

# Try different values for C
c_vals = np.arange(0.1, 1.5, 0.1)

paramgrid = {'C': c_vals, 'penalty': ['l1', 'l2']}

# Define fold parameters
kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Instantiate model
lr_sel = GridSearchCV(LogisticRegression(solver='saga'),
                      paramgrid,
                      cv=kf,
                      scoring='recall')

# Fit model to the training data
lr_sel.fit(X_sel_train_scaled, y_sel_train)

# Get tuned model params
lr_tuned = lr_sel.best_estimator_
lr_tuned

# Calculate area under the curve (AUC) for ROC
auc_lr_sel = roc_auc_score(y_sel_test,
                           lr_tuned.predict_proba(X_sel_test_scaled)[:, 1])
# Calculate fbeta
fbeta(lr_tuned, X_test=X_sel_test_scaled)

print('AUC = {}'.format(auc_lr_sel))

# Create an attribute for the feature names
lr_tuned.feature_names = X_sel.columns
lr_tuned.target_names = ['Fail', 'Success']

X_sel.columns

lr_tuned.feature_display_names = [
    'val_AnnualGrowthRate(%)', 'Norway', 'Latvia', 'A', 'Germany', 'Italy',
       'France', 'S', 'Italy', 'France', 'val_AnnualGrowthRate(%)'
]

# Pickle this for later

with open("/content/sample_data/lr_tuned.pkl", "wb") as f:
    pickle.dump(lr_tuned, f)

joblib.dump(lr_tuned,'lr_tuned.pkl')

# Intercept
lr_tuned.intercept_[0]

# convert intercept log-odds to probability
logodds = lr_tuned.intercept_
odds = np.exp(logodds)
prob = odds / (1 + odds)
prob[0]
print(
    'All else considered, companies that make it past their\
    val_AnnualGrowthRate(%), probability of success is {:.2f}%'
    .format(100 * prob[0]))

lr_tuned_coefs = pd.DataFrame(sorted(list(zip(X_sel.columns,
                                              lr_tuned.coef_[0])),
                                     key=(lambda x: x[1]),
                                     reverse=True),
                              columns=['Feature', 'Coefficient'])
lr_tuned_coefs['Odds'] = np.exp(lr_tuned_coefs.Coefficient)

# Plot coefficients
plt.barh(lr_tuned_coefs['Feature'], width=lr_tuned_coefs['Coefficient'])
plt.title('LogOdds')
plt.grid(b=False)
sns.despine()
# Save coefficients for plotting in Tableau
with open("lr_tuned_coefs.pkl", "wb") as f:
    pickle.dump(lr_tuned_coefs, f)

# Save coefficients for plotting in Tableau
with open("lr_tuned_coefs.pkl", "wb") as f:
    pickle.dump(lr_tuned_coefs, f)

startdataclass['val_AnnualGrowthRate(%)'].std()

lr_tuned_coefs

xgb_feats = sorted(list(zip(X.columns, xgb.feature_importances_)),
                   key=(lambda x: x[1]),
                   reverse=True)

X_sel_cols_xgb = [feat[0] for feat in xgb_feats if feat[1] > 0]



# Create new feature matrix
X_sel_xgb = X[X_sel_cols_xgb]

# Split the data with 80% to train and 20% to test
# Stratify to ensure train and test sets have 
# similar proportions of either target class
X_sel_xgb_train, X_sel_xgb_test, y_sel_xgb_train, y_sel_xgb_test = train_test_split(
    X_sel_xgb, y, test_size=0.2, random_state=40, stratify=y)

paramgrid = {
    'n_estimators': [1000],
    'max_depth': [9, 6, 9],
    'gamma': [0.5, 1, 1.5, 2, 5],
    'min_child_weight': [1, 5, 10],
    'subsample': [0.6, 0.8, 1.0],
    'colsample_bytree': [0.6, 0.8, 1.0]
}

# Define fold parameters
kf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)

lr_tuned.predict(X_sel_test_scaled)

annots = pd.DataFrame([['TN', 'FP'], ['FN', 'TP']])
type(annots)
annots

lr_confusion = confusion_matrix(y_sel_test, [
    1 if item[1] > 0.35 else 0
    for item in lr_tuned.predict_proba(X_sel_test_scaled)
])

sns.heatmap(lr_confusion,
            cmap=plt.cm.Blues,
            annot=True,
            square=True,
            xticklabels=['Fail', 'Success'],
            yticklabels=['Fail', 'Success'])  
b, t = plt.ylim()  # discover the values for bottom and top
b += 0.5  # Add 0.5 to the bottom
t -= 0.5  # Subtract 0.5 from the top
plt.ylim(b, t)  # update the ylim(bottom, top) values
plt.xlabel('Predicted Outcomes')
plt.ylabel('Actual Outcomes')
plt.show()

import pickle
import numpy as np
import pandas as pd

# lr_model is our simple logistic regression model
# lr_model.feature_names are the four different iris measurements
with open("/content/sample_data/lr_tuned.pkl","rb") as f:
    lr_model = pickle.load(f)

with open("/content/sample_data/scaler_sel.pkl","rb") as g:
    scaler = pickle.load(g)

feature_names = lr_model.feature_names
feature_display_names = lr_model.feature_display_names

def fund_extract(inputs):
    """
    Input:
    feature_dict: a dictionary of the form {"feature_name": "value"}
    Output:
    Returns list with the values corresponding to the first 4 feature columns
    """
    out = [float(inputs.get(name, 0)) for name in lr_model.feature_names[0:4]]
    out[1] *= 30
    out[2] *= 30
    return out

def convert(string,start,end):
    """
    Input: string for selected field, start/end index in feature column set
    Output: list of values corresponding to X_test[4:15]
    """
    vars = np.zeros(end-start)
    if string == "Other":
        return vars
    elif string in feature_names[start:end]:
        vars[list(feature_names[start:end]).index(string)] = 1
        return list(vars)

def make_prediction(x_input):
    """
    Input:
    feature_dict: a dictionary of the form {"feature_name": "value"}
    Function makes sure the features are fed to the model in the same order the
    model expects them.
    Output:
    Returns (x_inputs, probs) where
      x_inputs: a list of feature values in the order they appear in the model
      probs: a list of dictionaries with keys 'name', 'prob'
    """
    x_input_scaled = scaler.transform(np.array(x_input).reshape(1, -1))

# get is helpful - if somebody doesn't fill out one of the form entries then plug in zero
# a better guess than zero might be the average of that feature's distribution
# "if the key that is not found ==this, then plug in this"
    pred_probs = lr_model.predict_proba(x_input_scaled).flat

    probs = [{'name': lr_model.target_names[index], 'prob': pred_probs[index]}
    # list of dictionaries
    # dictionary comprehension
    # three dictionaries with two keys and two values each
    # can't sort within dictionaries, but can sort three separate dictionaries
             for index in np.argsort(pred_probs)[::-1]]
             # array sorted most likely to least likely class
             # 'name' gives the names of the classes
             # 'prob' gives its associated probability

    return probs

# This section checks that the prediction code runs properly
# To run, type "python predictor_api.py" in the terminal.
#
# The if __name__='__main__' section ensures this code only runs
# when running this file; it doesn't run when importing
if __name__ == '__main__':
    from pprint import pprint
    print("Checking to see what setting all params to 0 predicts")
    features = {f: '0' for f in feature_names}
    print('Features are')
    pprint(features)

    x_input, probs = make_prediction(features)
    print(f'Input values: {x_input}')
    print('Output probabilities')
    pprint(probs)





















































