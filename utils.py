from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors

import requests
import json

def create_pdf(df, name):
    """
    create a pdf for the dataframe

    :param df: any dataframe
    :type df: pandas.DataFrame

    :param name: name of the result pdf
    :type: str

    :return: None
    """
    # setup the canvas
    width = A4[0]
    styles = getSampleStyleSheet()

    # fillna with N.A.
    df = df.fillna("N.A.")

    # process content of the dataframe to make each element a paragraph object
    content = [list(i) for i in df.values]
    res_content = []
    for i in content:
        _temp = []
        for j in i:
            _temp.append(Paragraph(j, styles["Normal"]))
        res_content.append(_temp)

    # process header of the dataframe
    header = [Paragraph("<b>" + i + "</b>", styles["Normal"]) for i in df.columns.tolist()]

    # form the final list to be feed into table
    full_content = [header] + res_content

    # create the table and set format
    col_width = [(width - 10) / df.shape[1]] * df.shape[1]
    table = Table(full_content, colWidths=col_width)
    table.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))

    # foo pdf, just for getting the row sum
    # THIS IS GENIUS!!
    foo = canvas.Canvas("foo.pdf", pagesize=[width, 200000])

    # get the actual table height and page height, wrapOn function
    # will return the actual height and width of the table
    table_height = table.wrapOn(foo, width, 2000000)[1]
    page_height = table_height + 10

    # get the actual table height
    c = canvas.Canvas("{}.pdf".format(name), pagesize=[width, page_height])
    table.wrapOn(c, width, page_height)
    table.drawOn(c, 5, 5)
    c.save()

def shorten_url(url, url_shorten_api, url_shorten_workspace):
    """
    shorten url

    :param url: url to be shorten
    :type url: str

    :param url_shorten_api: URL Link Shortener API
    :type url_shorten_api: str

    :param url_shorten_workspace: URL Link Shortener workspace ID
    :type url_shorten_workspace: str

    :return: shortened url
    """

    linkRequest = {
        "destination": url,
        "domain": {"fullName": "rebrand.ly"}
    }

    requestHeaders = {
        "Content-type": "application/json",
        "apikey": url_shorten_api,
        "workspace": url_shorten_workspace
    }

    r = requests.post("https://api.rebrandly.com/v1/links",
                      data=json.dumps(linkRequest),
                      headers=requestHeaders)

    if (r.status_code == requests.codes.ok):
        link = r.json()
        return link["shortUrl"]
    else:
        return url