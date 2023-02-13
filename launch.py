from flask import Flask, render_template, request
from models import utils
import numpy as np
from sklearn.preprocessing import LabelEncoder
import json
import plotly
import plotly.express as px


df_students = utils.get_excel_file("student_predict")
result = df_students
df_predict = df_students
df_predict['alc'] = df_predict['Walc'] + df_predict['Dalc']

# Averaging three grades into one single grade
df_predict['G_Math'] = (df_predict['G1_Math'] + df_predict['G2_Math'] + df_predict['G3_Math']) / 3
df_predict['G_Por'] = (df_predict['G1_Por'] + df_predict['G2_Por'] + df_predict['G3_Por']) / 3

df_predict = df_predict.drop(columns=['school', 'address','Walc', 'Dalc', 'G1_Math', 'G2_Math', 'G3_Math', 'G1_Por', 'G2_Por', 'G3_Por'])

categorical_dict = {}
for col in df_predict.columns:
    # For each column of type object, use sklearn label encoder and add the mapping to a dictionary
    if df_predict[col].dtype == 'object':
        le = LabelEncoder() 
        df_predict[col] = le.fit_transform(df_predict[col])
        categorical_dict[col] = dict(zip(le.classes_, le.transform(le.classes_)))

# affichage de la page
model = utils.get_model("model_prediction_to_move_to_the_next_class")

predict =  model.predict(df_predict)
result['status'] = predict
result['status'] = result.status.apply(lambda x: 'admis' if x  == 1 else 'echec')
result = result.drop(columns=["G_Math", "G_Por"])
result_admis = result[result.status == 'admis']


app = Flask(__name__)


@app.route("/")
def index():
    # Create Bar chart for age
    age_grouped_ser = result_admis.groupby(['age'])['alc'].count()
    age_grouped_df = age_grouped_ser.reset_index()
    
    fig = px.bar(age_grouped_df, x='age', y='alc', color='age',
                 labels={
                     "age": "Age",
                     "alc": "Nombre d'étudiants",                 },
                 title="Nombre d’étudiants classés par âge qui iront en classe supérieur", 
                 barmode='group')
     
    # Create graphJSON
    graphJSON_age = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Create Bar chart for sex

    sex_grouped_ser = result_admis.groupby(['sex'])['alc'].count()
    sex_grouped_df = sex_grouped_ser.reset_index()
    
    fig = px.bar(sex_grouped_df, x='sex', y='alc', color='sex',
                 labels={
                     "sex": "Sexe",
                     "alc": "Nombre d'étudiants",                 },
                 title="Nombre d’étudiants classés par sexe qui iront en classe supérieur", 
                 barmode='group')
     
    # Create graphJSON
    graphJSON_sex = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    #List of  Mjob and Fjob who have job
    result_of_parent_who_have_job = result_admis[(result_admis.Mjob != 'at_home') & (result_admis.Fjob != 'at_home')]
    
    parent_who_have_job_grouped_ser = result_of_parent_who_have_job.groupby(['Mjob'])['alc'].count()
    job_grouped_df = parent_who_have_job_grouped_ser.reset_index()
    
    fig = px.bar(job_grouped_df, x='Mjob', y='alc', color='Mjob',
                 labels={
                     "Mjob": "Repartition selon le job de la mère",
                     "alc": "Nombre d'étudiants",                 },
                 title="Les étudiants dont les parents travails (MJob et FJob)  - (les deux parents travaillent)", 
                 barmode='group')
    
     
    # Create graphJSON
    graphJSON_Mjob = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    parent_who_have_job_grouped_ser = result_of_parent_who_have_job.groupby(['Fjob'])['alc'].count()
    job_grouped_df = parent_who_have_job_grouped_ser.reset_index()
    
    fig = px.bar(job_grouped_df, x='Fjob', y='alc', color='Fjob',
                 labels={
                     "Fjob": "Repartition selon le job du père",
                     "alc": "Nombre d'étudiants",                 },
                 title="Les étudiants dont les parents travails (MJob et FJob) - (les deux parents travaillent)", 
                 barmode='group')
    
     
    # Create graphJSON
    graphJSON_Fjob = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    #List of  Mjob and Fjob who don't have job
    result_of_parent_who_dont_have_job = result_admis[(result_admis.Mjob == 'at_home') & (result_admis.Fjob == 'at_home')]
    parent_who_dont_have_job_grouped_ser = result_of_parent_who_dont_have_job.groupby(['Mjob'])['alc'].count()
    dont_have_job_grouped_df = parent_who_dont_have_job_grouped_ser.reset_index()

    fig = px.bar(dont_have_job_grouped_df, x='Mjob', y='alc', color='Mjob',
                    labels={
                        "Mjob": "Repartition",
                        "alc": "Nombre d'étudiants",                 },
                    title="Les étudiants dont les parents ne travaillent (les deux parents sont à la maison)", 
                    barmode='group')
        
        
    # Create graphJSON
    graphJSON_Djob = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template('index.html', 
                           graphJSON_age = graphJSON_age, graphJSON_sex = graphJSON_sex ,
                           graphJSON_Mjob = graphJSON_Mjob, graphJSON_Fjob = graphJSON_Fjob, 
                           graphJSON_Djob = graphJSON_Djob)


@app.route("/student/")
def student():
    #List of students < 17
    select_result_colunms = result[['school', 'sex','age', 'Mjob', 'Fjob', 'absences_Math', 'absences_Por', 'alc',
                                    'paid', 'health', 'G1_Math', 'G2_Math', 'G3_Math', 'G1_Por', 'G2_Por', 'G3_Por', 'status']]

    result_age_lower_17 = select_result_colunms[select_result_colunms.age < 17]

    return render_template("student.html", results = utils.convert_df_html(result_age_lower_17))


if __name__ == "__main__":
    app.run(debug=True)
