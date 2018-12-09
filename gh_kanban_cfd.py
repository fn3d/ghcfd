import csv
from matplotlib import pyplot
from github import Github
import numpy
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


PROJECT_NAME = ''
USERNAME = ''
PASSWORD = ''
GITHUB_REPO = ''
EMAIL_PWD = ''
fromaddr = ''
recipients = ['']
SUBJECT = ''

g = Github(USERNAME, PASSWORD)
repo = g.get_repo(GITHUB_REPO)

board_card_dict = {}
current_card_dict = {}
projects = repo.get_projects()
project = None
column_find_criteria = ['Date', 'Backlog', 'To Do', 'In Progress',
                        'Verify', 'Done']

'''
get the current situation on the board and store it in the dict

'''
board_card_dict['Date'] = []
for proj in projects:
    if proj.name == PROJECT_NAME:
        project = proj
        columns = proj.get_columns()
        for column in columns:
            for criteria in column_find_criteria:
                if criteria.lower() in column.name.lower():
                    board_card_dict[criteria] = [column.name]
                    cards_count = len(list(column.get_cards()))
                    current_card_dict[criteria] = cards_count
        break

csv_file_read = open('file.csv', 'r', newline='')
csv_reader = csv.reader(csv_file_read, delimiter=',')
current_date = datetime.datetime.now().strftime("%Y-%m-%d")

last_row = None
for row in csv_reader:
    last_row = row

csv_file_write = open('file.csv', "a", newline='')
csv_writer = csv.writer(csv_file_write, delimiter=',')


'''
writing today's board status to the csv file

'''
if current_date == last_row[0]:
    temp_arr = []
    csv_file_read = open('file.csv', 'r', newline='')
    csv_reader = csv.reader(csv_file_read, delimiter=',')
    for row in csv_reader:
        temp_arr.append(row)
    csv_file_write = open('file.csv', 'w')
    csv_writer = csv.writer(csv_file_write, delimiter=',')
    for i in range(0, len(temp_arr)-1):
        csv_writer.writerow(temp_arr[i])

current_stats_write_arr = []
current_stats_write_arr.append(current_date)
current_stats_write_arr.append(current_card_dict['Backlog'])
current_stats_write_arr.append(current_card_dict['To Do'])
current_stats_write_arr.append(current_card_dict['In Progress'])
current_stats_write_arr.append(current_card_dict['Verify'])
current_stats_write_arr.append(current_card_dict['Done'])
csv_writer.writerow(current_stats_write_arr)
csv_file_write.close()

last_row = current_stats_write_arr

'''
read the current state on the csv file and store it in the dict

'''
dates_processed = False
for i in range(1, len(column_find_criteria)):
    board_card_dict[column_find_criteria[i]].append(0)
    row_count = 0
    csv_file_read = open('file.csv', 'r', newline='')
    csv_reader = csv.reader(csv_file_read, delimiter=',')
    for row in csv_reader:
        if dates_processed is False:
            board_card_dict['Date'].append(row[i-1])
        if row_count != 0:
            board_card_dict[column_find_criteria[i]].append(int(row[i]))
        row_count += 1
    if dates_processed is False:
        if current_date != last_row[0]:
            board_card_dict['Date'].append(current_date)
        dates_processed = True
    if current_date != last_row[0]:
        board_card_dict[column_find_criteria[i]].append \
                (current_card_dict[column_find_criteria[i]])

'''
use the information to plot the cumulative flow diagram by developing numpy
arrays from the board_card_dict

'''
if __name__ == '__main__':
    arr_backlog = board_card_dict['Backlog'][1:]
    arr_todo = board_card_dict['To Do'][1:]
    arr_inprog = board_card_dict['In Progress'][1:]
    arr_verify = board_card_dict['Verify'][1:]
    arr_done = board_card_dict['Done'][1:]
    arr_stack = numpy.row_stack((arr_done, arr_verify, arr_inprog, arr_todo,
                                 arr_backlog))
    days = numpy.arange(0, len(arr_backlog), 1)
    fig, ax = pyplot.subplots()
    ax.stackplot(days, arr_stack)
    plot_vert_height = max(numpy.sum(arr_stack, axis=0))

    pyplot.title('Cumulative Flow Diagram')
    ax.set_ylabel('Issues')
    ax.set_xlabel('Days')
    ax.set_xlim(0, len(arr_backlog) - 1)
    ax.set_ylim(0, plot_vert_height + plot_vert_height * 0.1)
    ax.legend(['Done', 'Verify', 'In Progress', 'To Do', 'Backlog'])
    plot_file_name = 'plot_' + str(current_date) + '.png'
    plot_file = pyplot.savefig(plot_file_name)
    pyplot.show()

    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    msg = MIMEMultipart()

    msg['From'] = fromaddr
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = SUBJECT + str(current_date)

    body = "Please find attached the Kanban Cumulative Flow Diagram for: " + str(current_date)

    msg.attach(MIMEText(body, 'plain'))

    filename = 'plot_' + datetime.datetime.now().strftime("%Y-%m-%d") + '.png'
    attachment = open(filename, "rb")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, EMAIL_PWD)
    text = msg.as_string()
    if (datetime.datetime.now().weekday() != 5) and \
       (datetime.datetime.now().weekday() != 6):
        server.sendmail(fromaddr, recipients, text)
    server.quit()

