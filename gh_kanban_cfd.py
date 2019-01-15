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


# please fill in the required information below prior
# to running the script.
CSV_FILE_NAME = ''
PROJECT_NAME = ''
USERNAME = ''
PASSWORD = ''
GITHUB_REPO = ''
EMAIL_PWD = ''
fromaddr = ''
recipients = ['']
SUBJECT = ''
COLUMN_FIND_CRITERIA = ['Date', 'To Do', 'In Progress',
                        'Verify', 'Done']
SEND_EMAIL = True


# todo_completion_forecast returns:
# (a) the overall issue completion rate
# (b) the number of remaining issues under To Do
# (c) the estimated completion date for the remaining issues
def todo_completion_forecast(arr_stack):
    num_days = len(arr_stack[0])
    completion_rate = round(arr_stack[0][num_days-1]/num_days, 3)
    current_todo_count = arr_stack[3][num_days-1]
    current_date = datetime.datetime.now()
    project_completion_days = \
            (num_days/arr_stack[0][num_days-1])*current_todo_count
    projected_completion_date = (current_date + \
            datetime.timedelta(days=project_completion_days)).strftime("%Y-%m-%d")
    return completion_rate, current_todo_count, projected_completion_date


# get the current situation on the board and store it in the dict
def pull_board_info():
    board_card_dict = {}
    board_card_dict['Date'] = []
    current_card_dict = {}
    for proj in projects:
        if proj.name == PROJECT_NAME:
            project = proj
            columns = proj.get_columns()
            for column in columns:
                for criteria in COLUMN_FIND_CRITERIA:
                    if criteria.lower() in column.name.lower():
                        board_card_dict[criteria] = [column.name]
                        cards_count = len(list(column.get_cards()))
                        current_card_dict[criteria] = cards_count
            break
    return board_card_dict, current_card_dict


# writing today's board status to the csv file
def write_board_to_csv(current_date, last_row, current_card_dict):
    csv_file_write = open(CSV_FILE_NAME, "a", newline='')
    csv_writer = csv.writer(csv_file_write, delimiter=',')

    if current_date == last_row[0]:
        temp_arr = []
        csv_file_read = open(CSV_FILE_NAME, 'r', newline='')
        csv_reader = csv.reader(csv_file_read, delimiter=',')
        for row in csv_reader:
            temp_arr.append(row)
        csv_file_write = open(CSV_FILE_NAME, 'w')
        csv_writer = csv.writer(csv_file_write, delimiter=',')
        for i in range(0, len(temp_arr)-1):
            csv_writer.writerow(temp_arr[i])

    current_stats_write_arr = []
    current_stats_write_arr.append(current_date)
    for item in current_card_dict:
        current_stats_write_arr.append(current_card_dict[item])
    csv_writer.writerow(current_stats_write_arr)
    csv_file_write.close()


def pull_updated_csv_info(current_date, last_row, board_card_dict):
    # read the current state on the csv file and store it in the dict
    dates_processed = False
    for i in range(1, len(COLUMN_FIND_CRITERIA)):
        board_card_dict[COLUMN_FIND_CRITERIA[i]].append(0)
        row_count = 0
        csv_file_read = open(CSV_FILE_NAME, 'r', newline='')
        csv_reader = csv.reader(csv_file_read, delimiter=',')
        for row in csv_reader:
            if dates_processed is False:
                board_card_dict['Date'].append(row[i-1])
            if row_count != 0:
                board_card_dict[COLUMN_FIND_CRITERIA[i]].append(int(row[i]))
            row_count += 1
        if dates_processed is False:
            if current_date != last_row[0]:
                board_card_dict['Date'].append(current_date)
            dates_processed = True
        if current_date != last_row[0]:
            board_card_dict[COLUMN_FIND_CRITERIA[i]].append \
                    (current_card_dict[COLUMN_FIND_CRITERIA[i]])
    return board_card_dict


# use the information to plot the cumulative flow diagram 
# by developing numpy arrays from the board_card_dict
def create_cfd(board_historic_dict):
    arr_group = []
    for i in reversed(COLUMN_FIND_CRITERIA):
        if (i != 'Date'):
            arr_group.append(board_historic_dict[i][1:])
    arr_stack = numpy.row_stack((arr_group))
    days = numpy.arange(0, len(arr_group[1]), 1)
    fig, ax = pyplot.subplots()
    ax.stackplot(days, arr_stack)
    plot_vert_height = max(numpy.sum(arr_stack, axis=0))

    pyplot.title('Cumulative Flow Diagram')
    ax.set_ylabel('Issues')
    ax.set_xlabel('Days')
    ax.set_xlim(0, len(arr_group[0]) - 1)
    ax.set_ylim(0, plot_vert_height + plot_vert_height * 0.1)
    ax.legend([COLUMN_FIND_CRITERIA[i] for i in
               range(len(COLUMN_FIND_CRITERIA)-1, 0, -1)])
    plot_file_name = 'plot_' + str(current_date) + '.png'
    plot_file = pyplot.savefig(plot_file_name)
    pyplot.show()
    return arr_group


def push_email_update(current_date):
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = SUBJECT + str(current_date)

    body = "Please find attached the Kanban Cumulative Flow Diagram for: " + \
            str(current_date)
    body_new_line = "<br><br>"
    body_completion_rate = "Overall issues completion rate = " + \
            str(completion_rate)
    body_todo_count = "Planned items in To Do = " + str(todo_count)
    body_completion_date = "Expected planned items completion by: " + \
            str(completion_date)
    msg.attach(MIMEText(body, 'html'))
    msg.attach(MIMEText(body_new_line, 'html'))
    msg.attach(MIMEText(body_completion_rate, 'html'))
    msg.attach(MIMEText(body_new_line, 'html'))
    msg.attach(MIMEText(body_todo_count, 'html'))
    msg.attach(MIMEText(body_new_line, 'html'))
    msg.attach(MIMEText(body_completion_date, 'html'))
    msg.attach(MIMEText(body_new_line, 'html'))

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


if __name__ == '__main__':
    if (datetime.datetime.now().weekday() != 5) and \
        (datetime.datetime.now().weekday() != 6):
        g = Github(USERNAME, PASSWORD)
        repo = g.get_repo(GITHUB_REPO)
        projects = repo.get_projects()
        project = None

        board_template_dict, current_card_dict = pull_board_info()

        csv_file_read = open(CSV_FILE_NAME, 'r', newline='')
        csv_reader = csv.reader(csv_file_read, delimiter=',')
        last_row = None
        for row in csv_reader:
            last_row = row

        current_date = datetime.datetime.now().strftime("%Y-%m-%d")

        write_board_to_csv(current_date, last_row, current_card_dict)
        last_row = [current_card_dict[item] for item in current_card_dict]
        last_row.insert(0, current_date)
        board_historic_dict = pull_updated_csv_info(current_date, last_row, \
                                                board_template_dict)
        arr_group = create_cfd(board_historic_dict)
        completion_rate, todo_count, completion_date = \
                todo_completion_forecast(arr_group)

        if SEND_EMAIL:
            push_email_update(current_date)
