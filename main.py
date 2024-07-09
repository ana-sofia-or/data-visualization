from os.path import dirname, join
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput, Spacer
from bokeh.plotting import figure

students = pd.read_csv(join(dirname(__file__), "student-scores.csv"))
students['color'] = students['gender'].apply(lambda x: "blue" if x == "male" else "pink")
students.fillna(0, inplace=True)

yaxis_map = {
    "Absence Days": "absence_days",
    "Extracurricular Activities": "extracurricular_activities",
    "Weekly Self Study Hours": "weekly_self_study_hours",
}

xaxis_map = {
    "Math Score": "math_score",
    "History Score": "history_score",
    "Physics Score": "physics_score",
    "Chemistry Score": "chemistry_score",
    "Biology Score": "biology_score",
    "English Score": "english_score",
    "Geography Score": "geography_score",
}

desc = Div(text=open(join(dirname(__file__), "description.html")).read(), sizing_mode="stretch_width")
with open(join(dirname(__file__), "conclusion.html"), "r", encoding="utf-8") as file:
    html_content = file.read()
conclusion = Div(text=html_content, sizing_mode="stretch_width")

absence_days_start = Slider(title="Absence Days", value=students.absence_days.min(),
                            start=students.absence_days.min(), end=students.absence_days.max(), step=1)
absence_days_end = Slider(title="Absence Days", value=students.absence_days.max(),
                          start=students.absence_days.min(), end=students.absence_days.max(), step=1)
weekly_self_study_hours_start = Slider(title="Weekly Self Study Hours", start=students.weekly_self_study_hours.min(),
                                       end=students.weekly_self_study_hours.max(),
                                       value=students.weekly_self_study_hours.min(), step=1)
weekly_self_study_hours_end = Slider(title="Weekly Self Study Hours", start=students.weekly_self_study_hours.min(),
                                     end=students.weekly_self_study_hours.max(),
                                     value=students.weekly_self_study_hours.max(), step=1)
gender = Select(title="Gender", value="All", options=["All", "male", "female"])
part_time_job = Select(title="Part-Time Job", value="All", options=["All", "True", "False"])
first_name = TextInput(title="First names contains")
last_name = TextInput(title="Last names contains")
x_axis = Select(title="X Axis", options=sorted(xaxis_map.keys()), value="Math Score")
y_axis = Select(title="Y Axis", options=sorted(yaxis_map.keys()), value="Weekly Self Study Hours")

source = ColumnDataSource(
    data=dict(x=[], y=[], color=[], gender=[], absence_days=[], weekly_self_study_hours=[], alpha=[], first_name=[],
              last_name=[], x_axis=[], y_axis=[]))

tooltips = [
    ("first_name", "@first_name"),
    ("gender", "@gender"),
]

p = figure(height=600, title="", toolbar_location="right", tooltips=tooltips, sizing_mode="stretch_width")
p.scatter(x="x", y="y", source=source, size=7, color="color", line_color=None)
p.background_fill_color = "beige"


def select_students():
    gender_val = gender.value.lower()
    part_time_job_val = part_time_job.value.lower()
    first_name_val = first_name.value.lower()
    last_name_val = last_name.value.lower()
    students['part_time_job'] = students['part_time_job'].astype(str)
    selected = students[
        (students.absence_days >= absence_days_start.value) & (students.absence_days <= absence_days_end.value) &
        (students.weekly_self_study_hours >= weekly_self_study_hours_start.value) & (
                    students.weekly_self_study_hours <= weekly_self_study_hours_end.value)
        ]
    if gender_val != "all":
        selected = selected[selected.gender.str.lower() == gender_val]
    if part_time_job_val != "all":
        selected = selected[selected.part_time_job.str.lower().str.contains(part_time_job_val)]
    if first_name_val != "":
        selected = selected[selected.first_name.str.lower().str.contains(first_name_val)]
    if last_name_val != "":
        selected = selected[selected.last_name.str.lower().str.contains(last_name_val)]
    return selected


def update():
    df = select_students()
    x_name = xaxis_map[x_axis.value]
    y_name = yaxis_map[y_axis.value]

    p.xaxis.axis_label = x_axis.value
    p.yaxis.axis_label = y_axis.value
    p.title.text = f"{len(df)} students selected"

    source.data = dict(
        x=df[x_name],
        y=df[y_name],
        color=df["color"],
        gender=df["gender"],
        first_name=df["first_name"],
        absence_days=df["absence_days"],
        part_time_job=df["part_time_job"],
        extracurricular_activities=df["extracurricular_activities"],
        weekly_self_study_hours=df["weekly_self_study_hours"],
        career_aspiration=df["career_aspiration"],
        math_score=df["math_score"],
        history_score=df["history_score"],
        physics_score=df["physics_score"],
        chemistry_score=df["chemistry_score"],
        biology_score=df["biology_score"],
        english_score=df["english_score"],
        geography_score=df["geography_score"],
    )


controls = [gender, first_name, last_name, absence_days_start, absence_days_end,
            weekly_self_study_hours_start, weekly_self_study_hours_end, part_time_job, x_axis, y_axis]

for control in controls:
    control.on_change("value", lambda attr, old, new: update())

inputs = column(*controls, width=400, height=800)

layout = column(desc, row(inputs, p, sizing_mode="stretch_both"), conclusion,
                sizing_mode="stretch_width", height=850, margin=(30, 30, 0, 30))

update()

curdoc().add_root(layout)
curdoc().title = "Students Explorer"
