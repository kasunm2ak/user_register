import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from flask import Flask, render_template, request, url_for, flash, send_file
from werkzeug.utils import redirect
from flask_mysqldb import MySQL


from reportlab.pdfgen import canvas
import pandas as pd
import pymysql
from flask import make_response
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = 'sdefgrgddfcdcthtvfr'
app.config['MYSQL_HOST'] = '172.22.110.35'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root123'
app.config['MYSQL_PORT'] = 5600
app.config['MYSQL_DB'] = 'OSS_USERS'

mysql = MySQL(app)


@app.route('/')
def Index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user_request")
    data = cur.fetchall()
    cur.close()
    print("fdrefrgtrtgt")
    return render_template('index.html', dataArray=data)


@app.route('/insert', methods=['POST'])
def insert():
    print(request)
    if request.method == "POST":
        flash("Data Inserted Successfully")
        namewinitial = request.form['NameWinitial']
        username = request.form['UserName']
        designation = request.form['Designation']
        servicenum = request.form['ServiceNum']
        requestermob = request.form['RequesterMob']
        email = request.form['email']
        idnum = request.form['idnum']
        userip = request.form['userip']
        division = request.form['division']
        selected_options = request.form.getlist('option')
        selected_options_str = ','.join(selected_options)
        selected_options_role = request.form.getlist('option_role')
        selected_options_role_str = ','.join(selected_options_role)
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO user_request (namewinitial,username,designation,servicenum,requestermob,email,idnum,userip,division,node,role) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (namewinitial, username, designation, servicenum, requestermob, email, idnum, userip, division,
             selected_options_str,
             selected_options_role_str))
        mysql.connection.commit()

        return redirect(url_for('Index'))


@app.route('/delete/<string:id_data>', methods=['GET'])
def delete(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM user_request WHERE namewinitial=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('Index'))


@app.route('/update', methods=['POST', 'GET'])
def update():
    if request.method == 'POST':
        namewinitial = request.form['NameWinitial']
        username = request.form['UserName']
        designation = request.form['Designation']
        servicenum = request.form['ServiceNum']
        requestermob = request.form['RequesterMob']
        email = request.form['email']
        idnum = request.form['idnum']
        userip = request.form['userip']
        division = request.form['division']
        selected_options = request.form.getlist('option')
        selected_options_str = ','.join(selected_options)
        selected_options_role = request.form.getlist('option_role')
        selected_options_role_str = ','.join(selected_options_role)
        cur = mysql.connection.cursor()
        # print(shortCode,reservedBy,usedPurpose,RequesterName,RequesterMob,Date)
        cur.execute("""
        UPDATE user_request SET username=%s,designation=%s,servicenum=%s,requestermob=%s,email=%s,idnum=%s,userip=%s,division=%s,node=%s,role=%s
        WHERE namewinitial=%s
        """, (username, designation, servicenum, requestermob, email, idnum, userip, division, selected_options_str,
              selected_options_role_str, namewinitial))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('Index'))


@app.route('/generate_pdf', methods=['GET'])

def generate_pdf():
    #url = id
    #numid = re.search(r'\d+', url).group()
    # Fetch data from the database (replace this with your query)\
    num = request.args.get('servicenum')
    #print("now here")
    #print(num)
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user_request WHERE servicenum=%s", (num,))
    data = cur.fetchall()
    #print(data)
    cur.close()

    # Generate PDF
    pdf_filename = 'output.pdf'
    response = make_response(generate_pdf_report(data))
    response.headers['Content-Disposition'] = f'attachment; filename={pdf_filename}'
    response.headers['Content-Type'] = 'application/pdf'
    #return redirect(url_for('Index'))

    return response


def generate_pdf_report(data):
    # Use ReportLab to create a PDF document
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Write data to the PDF (customize this based on your data structure)
    table_data = [['Field', 'Value']]

    for row in data:
        for field, value in zip(['Name With Initial', 'User Name', 'Designation', 'Service Number', 'Requester Mobile', 'Email', 'ID Num', 'USER IP', 'USER DIVISION', 'Node', 'Role'], row):
            table_data.append([field, str(value)])

    # Create a table from the data
    table = Table(table_data)

    # Add style to the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ROTATE', (0, 0), (-1, -1), 90),
    ])

    table.setStyle(style)

    # Build the PDF document
    doc.build([table])

    buffer.seek(0)
    return buffer


if __name__ == '__main__':
    print("rfrrrr")
    app.run(port=5001, threaded=True, host=('0.0.0.0'))
