# -*- coding: utf-8 -*-
"""main.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1piLKc93nvN0JJjxsL4SyjebhOmcAkmc-

#Installing Pyspark
"""

pip install pyspark

"""#Importing libraries"""

from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml import Pipeline
from pyspark.ml.feature import StandardScaler
from pyspark.ml.classification import RandomForestClassifier, DecisionTreeClassifier, GBTClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

"""#Creating spark session"""

spark = SparkSession.builder.appName("DiabetesPrediction").getOrCreate()

"""# Loading the Dataset"""

dataset_path = "Healthcare_dataset.csv"
df = spark.read.csv(dataset_path, header=True, inferSchema=True)

df

"""# Checking for null values in the DataFrame"""

from pyspark.sql.functions import col
null_columns = [col(column) for column in df.columns if df.filter(col(column).isNull()).count() > 0]
if null_columns:
    print("Warning: There are null values in the following columns:")
    for column in null_columns:
        print(column)
else:
    print("No null values in the dataset.")

"""#Data Preprocessing

## Converting categorical columns to numerical representations
"""

from pyspark.ml.feature import VectorAssembler, StandardScaler, StringIndexer, OneHotEncoder
gender_indexer = StringIndexer(inputCol="gender", outputCol="gender_index")
smoking_indexer = StringIndexer(inputCol="smoking_history", outputCol="smoking_index")

"""## One-hot encoding the indexed categorical columns"""

gender_encoder = OneHotEncoder(inputCol="gender_index", outputCol="gender_encoded")
smoking_encoder = OneHotEncoder(inputCol="smoking_index", outputCol="smoking_encoded")

"""## Assembling all features into a single vector"""

feature_columns = ["age", "hypertension", "heart_disease", "bmi", "HbA1c_level", "blood_glucose_level",
                   "gender_encoded", "smoking_encoded"]
assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")

# Standardize features
scaler = StandardScaler(inputCol="features", outputCol="scaled_features")
# Create a pipeline for preprocessing
preprocessing_pipeline = Pipeline(stages=[gender_indexer, smoking_indexer, gender_encoder, smoking_encoder, assembler, scaler])
# Fit and transform the data
preprocessed_data = preprocessing_pipeline.fit(df).transform(df)

"""# Visualizations

# Pairplot Visualization
"""

target_column = 'diabetes'
feature_columns_without_features = [col for col in feature_columns if col != 'features']
pandas_df = preprocessed_data.select(feature_columns_without_features + [target_column]).toPandas()
sns.pairplot(pandas_df, hue=target_column)
plt.title("Pairplot of Features")
plt.show()

"""# Visualization of Correlation Matrix"""

corr_matrix = pandas_df.corr()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
plt.title("Correlation Matrix")
plt.show()

"""# Visualization of Bar Plot of Target Variable Distribution"""

plt.figure(figsize=(6, 4))
sns.countplot(x=target_column, data=pandas_df)
plt.title("Distribution of Target Variable")
plt.show()

"""# Visualization of Box Plot of Age by Target Variable"""

plt.figure(figsize=(8, 6))
sns.boxplot(x=target_column, y='age', data=pandas_df)
plt.title("Box Plot of Age by Target Variable")
plt.show()

"""# Visualization of Distribution of BMI by Target Variable"""

plt.figure(figsize=(8, 6))
sns.boxplot(x=target_column, y='bmi', data=pandas_df)
plt.title("Distribution of BMI by Target Variable")
plt.show()

"""# Visualization of Blood Glucose Level Distribution by Target Variable"""

plt.figure(figsize=(8, 6))
sns.boxplot(x=target_column, y='blood_glucose_level', data=pandas_df)
plt.title("Blood Glucose Level Distribution by Target Variable")
plt.show()

"""# Visualization of HbA1c Level Distribution by Target Variable"""

plt.figure(figsize=(8, 6))
sns.boxplot(x=target_column, y='HbA1c_level', data=pandas_df)
plt.title("HbA1c Level Distribution by Target Variable")
plt.show()

"""# Checking unique values in the 'smoking_history' column"""

unique_smoking_history = preprocessed_data.select('smoking_history').distinct().rdd.flatMap(lambda x: x).collect()
print("Unique Smoking History Values:", unique_smoking_history)

"""# Visualization of Blood Glucose Level vs. BMI Scatter Plot"""

plt.figure(figsize=(10, 8))
sns.scatterplot(x='blood_glucose_level', y='bmi', hue=target_column, data=pandas_df)
plt.title("Blood Glucose Level vs. BMI Scatter Plot")
plt.show()

"""# Visualization of Blood Glucose Level vs. HbA1c Level Scatter Plot with Target Variable"""

plt.figure(figsize=(10, 8))
sns.scatterplot(x='blood_glucose_level', y='HbA1c_level', hue=target_column, data=pandas_df)
plt.title("Blood Glucose Level vs. HbA1c Level Scatter Plot with Target Variable")
plt.show()

"""# Visualization of Distribution of BMI by Hypertension Status"""

plt.figure(figsize=(10, 6))
sns.boxplot(x='hypertension', y='bmi', data=pandas_df)
plt.title("Distribution of BMI by Hypertension Status")
plt.show()

"""# Implementing Machine Learning Models

## Train test spliting
"""

train_data, test_data = preprocessed_data.randomSplit([0.8, 0.2], seed=42)

"""#Creating random forest, decision tree, Gradient-Boosted Tree classifier models"""

from pyspark.ml.classification import LogisticRegression
target_column = 'diabetes'
# Random Forest Classifier
rf = RandomForestClassifier(labelCol=target_column, featuresCol='features', numTrees=60)
# Decision Tree Classifier
dt = DecisionTreeClassifier(labelCol=target_column, featuresCol='features')
# Gradient-Boosted Tree Classifier
gbt = GBTClassifier(labelCol=target_column, featuresCol='features', maxIter=10)
# Building the parameter grid for the CrossValidator
paramGrid = (ParamGridBuilder()
             .addGrid(rf.numTrees, [50, 100])
             .build())

"""## Fiting the models"""

rf_model = rf.fit(train_data)
dt_model = dt.fit(train_data)
gbt_model = gbt.fit(train_data)

"""## Evaluation on Random Forest Model"""

from pyspark.ml.evaluation import MulticlassClassificationEvaluator
rf_predictions = rf_model.transform(test_data)
rf_evaluator = MulticlassClassificationEvaluator(labelCol=target_column, metricName='accuracy')
rf_accuracy = rf_evaluator.evaluate(rf_predictions)
print(f"Random Forest Accuracy: {rf_accuracy}")

"""## Evaluation on Decision Tree Model"""

dt_predictions = dt_model.transform(test_data)
dt_evaluator = MulticlassClassificationEvaluator(labelCol=target_column, metricName='accuracy')
dt_accuracy = dt_evaluator.evaluate(dt_predictions)
print(f"Decision Tree Accuracy: {dt_accuracy}")

"""## Evaluation on Gradient-Boosted Tree Model"""

gbt_predictions = gbt_model.transform(test_data)
gbt_evaluator = MulticlassClassificationEvaluator(labelCol=target_column, metricName='accuracy')
gbt_accuracy = gbt_evaluator.evaluate(gbt_predictions)
print(f"Gradient-Boosted Tree Accuracy: {gbt_accuracy}")

"""##Showing prediction for GBT Model"""

gbt_predictions = gbt_model.transform(test_data)
# Selecting relevant columns for display
result_df = gbt_predictions.select('features', 'diabetes', 'prediction', 'probability').toPandas()
# Displaying the Pandas DataFrame
result_df

"""##Showing prediction for DT model"""

dt_predictions = dt_model.transform(test_data)
# Selecting relevant columns for display
result_df = dt_predictions.select('features', 'diabetes', 'prediction', 'probability').toPandas()
# Displaying the Pandas DataFrame
result_df

"""## Showing prediction for Random Forest model"""

rf_predictions = rf_model.transform(test_data)
# Selecting relevant columns for display
result_df = rf_predictions.select('features', 'diabetes', 'prediction', 'probability').toPandas()
# Displaying the Pandas DataFrame
result_df