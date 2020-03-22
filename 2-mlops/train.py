import platform
import pandas as pd
import sklearn
import numpy as np
import os
from sklearn.externals import joblib
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder
from sklearn import tree
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn_pandas import DataFrameMapper
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from azureml.core import Run, Dataset, Workspace
from sklearn.metrics import accuracy_score
from azureml.contrib.interpret.explanation.explanation_client import ExplanationClient
from azureml.core.run import Run
from interpret.ext.blackbox import TabularExplainer
from azureml.contrib.interpret.visualize import ExplanationDashboard

def main():
    ws = Run.get_context().experiment.workspace
    os.makedirs('./outputs', exist_ok=True)
    df = Dataset.get_by_name(ws,'telcochurn').to_pandas_dataframe() 
    df = df.dropna(how="all")  # remove samples with all missing values
    df["Churn_numerical"] = df["Churn"]   
    target = df["Churn"]
    total_charges_filter = df.TotalCharges == " "
    df = df[~total_charges_filter]
    df.TotalCharges = pd.to_numeric(df.TotalCharges)
    df = df.drop(['Churn_numerical','Churn','customerID'], axis=1)
    train_model(df, target)
    run = Run.get_context()
    model = run.register_model(model_name='Churn_model', model_path='outputs/classifier.pkl')


def train_model(df, target):
    # Creating dummy columns for each categorical feature
    categorical = []
    for col, value in df.iteritems():
        if value.dtype == 'object':
            categorical.append(col)
    # Store the numerical columns in a list numerical
    numerical = df.columns.difference(categorical)
    numeric_transformations = [([f], Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())])) for f in numerical]
    categorical_transformations = [([f], OneHotEncoder(handle_unknown='ignore', sparse=False)) for f in categorical]
    transformations = numeric_transformations + categorical_transformations
    # Append classifier to preprocessing pipeline
    clf = Pipeline(steps=[('preprocessor', DataFrameMapper(transformations)),
                      ('classifier', LogisticRegression(solver='lbfgs'))])
    # Split data into train and test
    x_train, x_test, y_train, y_test = train_test_split(df,target, test_size=0.35, random_state=0, stratify=target)
    clf.fit(x_train, y_train)
    y_pred = clf.predict(x_test)
    print(classification_report(y_test, y_pred))
    accu = accuracy_score(y_test, y_pred)
    model_file_name = 'classifier.pkl'
    # save model in the outputs folder so it automatically get uploaded
    with open(model_file_name, 'wb') as file:
        joblib.dump(value=clf, filename=os.path.join('./outputs/', model_file_name))
    run = Run.get_context()
    run.log("accuracy", accu)
    # we upload the model into the experiment artifact store, but do not register it as a model until unit tests are sucessfully passed in next ML step
    run.upload_file(model_file_name, os.path.join('./outputs/', model_file_name)) 
    #Interpret steps
    client = ExplanationClient.from_run(run)
    # Using SHAP TabularExplainer
    explainer = TabularExplainer(clf.steps[-1][1], 
                             initialization_examples=x_train, 
                             features=df.columns, 
                             classes=["Not leaving", "leaving"], 
                             transformations=transformations)
    # explain overall model predictions (global explanation)
    global_explanation = explainer.explain_global(x_test)
    # Sorted SHAP values
    print('ranked global importance values: {}'.format(global_explanation.get_ranked_global_values()))
    # Corresponding feature names
    print('ranked global importance names: {}'.format(global_explanation.get_ranked_global_names()))
    # Feature ranks (based on original order of features)
    print('global importance rank: {}'.format(global_explanation.global_importance_rank))
    # uploading global model explanation data for storage or visualization in webUX
    # the explanation can then be downloaded on any compute 
    # multiple explanations can be uploaded
    client.upload_model_explanation(global_explanation, comment='global explanation: all features')
    # or you can only upload the explanation object with the top k feature info
    #client.upload_model_explanation(global_explanation, top_k=2, comment='global explanation: Only top 2 features')

main()