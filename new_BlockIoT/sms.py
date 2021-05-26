import smtplib, time
carriers = ['@mms.att.net','@tmomail.net','@vtext.com','@page.nextel.com']

def send(message,contract):
	print("Please add credentials!")
	return
	config = ast.literal_eval(contract.functions.get_config_file().call())
	# Replace the number with your own, or consider using an argument\dict for multiple people.
	for carrier in carriers:
		to_number = config["communication"]["phone"] + carrier
		auth = ('EMAIL', 'PASS')

		# Establish a secure session with gmail's outgoing SMTP server using your gmail account
		server = smtplib.SMTP( "smtp.gmail.com", 587 )
		server.starttls()
		server.login(auth[0], auth[1])

		# Send text message through SMS gateway of destination number
		server.sendmail( auth[0], to_number, message)
		time.sleep(2)