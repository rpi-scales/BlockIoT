import os


def send(to, message):
    with open("new_BlockIoT/sms/message.scpt","r") as f:
        data = f.read()
        data = data.replace('**phone_number**', to)
        data = data.replace('**message**', message)
    with open("new_BlockIoT/sms/message.scpt","w") as f:
        f.write(data)
    f.close()
    os.system("osascript new_BlockIoT/sms/message.scpt")
    data = data.replace(to,'**phone_number**')
    data = data.replace(message,'**message**')
    with open("new_BlockIoT/sms/message.scpt","w") as f:
        f.write(data)
    f.close()
