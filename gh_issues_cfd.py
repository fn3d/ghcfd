import csv
from matplotlib import pyplot
from github import Github
import numpy
import datetime
import pickle


USERNAME = ''
PASSWORD = ''
GITHUB_REPO = ''
PLOT_TITLE = ''

g = Github(USERNAME, PASSWORD)
repo = g.get_repo(GITHUB_REPO)

weeks_arr = []
issues_dump = None
try:
    issues_dump = pickle.load(open("issues_dump", "rb"))
except Exception:
    issues_dump = None
if issues_dump == None:
    issues_arr_dump = []
    issues = repo.get_issues("*", "closed")
    for issue in issues:
        issues_arr_dump.append(issue)
    issues = repo.get_issues("none", "closed")
    for issue in issues:
        issues_arr_dump.append(issue)
    issues = repo.get_issues("none", "open")
    for issue in issues:
        issues_arr_dump.append(issue)
    issues = repo.get_issues("*", "open")
    for issue in issues:
        issues_arr_dump.append(issue)
    pickle.dump(issues_arr_dump, open("issues_dump", "wb"))
issues_dump = pickle.load(open("issues_dump", "rb"))
issues_dump.reverse()

max_issue_num = 0
max_issue = None
min_issue = None
for issue in issues_dump:
    if issue.number > max_issue_num:
        max_issue_num = issue.number
        max_issue = issue
    if issue.number == 1:
        min_issue = issue

proj_start_date = min_issue.created_at
proj_end_date = max_issue.created_at

proj_start_week_date = proj_start_date
if proj_start_date.weekday() != 0:
    proj_start_week_date -= \
            datetime.timedelta(days=proj_start_date.weekday())

current_date = datetime.datetime.now()
proj_end_week_date = current_date
if proj_end_date.weekday() != 4:
    proj_end_week_date += \
            datetime.timedelta(days=4-proj_end_date.weekday())

last_week_start_date = proj_end_week_date - datetime.timedelta(days=4)

date_inc = proj_start_week_date
week_open_accum = 0
week_closed_accum = 0
current_week_start_date = None
while date_inc <= last_week_start_date:
    if date_inc.weekday() == 0:
        current_week_start_date = date_inc
    counter = 0
    while counter < len(issues_dump):
        current_week_end_date = current_week_start_date + \
                datetime.timedelta(days=7)
        if (issues_dump[counter].created_at >= current_week_start_date) and \
           (issues_dump[counter].created_at <= current_week_end_date):
            if (issues_dump[counter].state != 'closed'):
                week_open_accum += 1
        if issues_dump[counter].state == 'closed':
            if (issues_dump[counter].closed_at >= current_week_start_date) and \
                (issues_dump[counter].closed_at <= current_week_end_date):
                week_closed_accum += 1
        counter += 1
    weeks_arr.append([current_week_start_date.strftime('%Y-%m-%d'),
                               current_week_end_date.strftime('%Y-%m-%d'),
                               week_open_accum, week_closed_accum])
    date_inc += datetime.timedelta(days=7)

arr_opened = [item[2] for item in weeks_arr]
arr_closed = [item[3] for item in weeks_arr]
arr_stack = numpy.row_stack((arr_closed, arr_opened))

weeks = numpy.arange(0, len(arr_opened), 1)
fig, ax = pyplot.subplots()
ax.stackplot(weeks, arr_stack)
plot_vert_height = max(numpy.sum(arr_stack, axis=0))

pyplot.title(PLOT_TITLE)
ax.set_ylabel('Issues')
ax.set_xlabel('Weeks')
ax.set_xlim(0, len(weeks_arr) - 1)
ax.set_ylim(0, plot_vert_height + plot_vert_height * 0.1)
ax.legend(['Closed', 'Opened'])
plot_file_name = 'gh_issues_plot_' + str(current_date.strftime('%Y-%m-%d')) + '.png'
plot_file = pyplot.savefig(plot_file_name)
pyplot.show()
