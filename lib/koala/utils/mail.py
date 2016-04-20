#!/usr/bin/env python
# -*- coding: utf-8 -*-

from email.Utils import formatdate
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import datetime
import os
from koala.utils import show_error_message

from koala.config import Configuration
config = Configuration()

# TODO: take the smtp configuration from galaxy's config.ini file
# TODO: review exception rules


def get_message_email(tool_name):
    try:
        now = datetime.datetime.now()
        tupla = now.timetuple()
        data = str(
            tupla[2]) + '/' + str(tupla[1]) + '/' + \
            str(tupla[0]) + ' ' + str(tupla[3]) + ':' + str(tupla[4]) + ':' + str(tupla[5])

        tool_name = tool_name.replace('_', ' ')

        messageEmail = '''Hi,

        Your simulation has been conclued at ''' + data + '''.

        You have to go to your History and download it.

        Best Regards.

        %s''' % tool_name

        return messageEmail

    except Exception, e:
        show_error_message("Error while getMessageEmail email!\n%s" % e)


def send_email(de, para, assunto, mensagem, arquivos, servidor):

        try:
            # Cria o objeto da mensagem
            msg = MIMEMultipart()
            # Define o cabeçalho
            msg['From'] = de
            msg['To'] = para
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = assunto

            # Atacha o texto da mensagem
            msg.attach(MIMEText(mensagem))

            # Atacha os arquivos
            for arquivo in arquivos:
                parte = MIMEBase('application', 'octet-stream')
                parte.set_payload(open(arquivo, 'rb').read())
                encoders.encode_base64(parte)
                parte.add_header(
                    'Content-Disposition', 'attachment; filename="%s"' % os.path.basename(arquivo))
                msg.attach(parte)

            # Conecta ao servidor SMTP
            smtp = smtplib.SMTP(servidor, config.getint('smtp_port', 587))
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            # Faz login no servidor
            smtp.login(config.get('email_address', None), config.get('email_password', None))
            try:
                # Envia o e-mail
                smtp.sendmail(de, para, msg.as_string())
            finally:
                # Desconecta do servidor
                smtp.close()
        except Exception, e:
            show_error_message("Error when SendEmail:\n%s" % e)
