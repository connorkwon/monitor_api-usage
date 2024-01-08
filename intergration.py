import ses


def ses_send(content, recipients, is_monthly):
    if is_monthly:
        word = '[Monthly]'
    else:
        word = '[Daily]'
    sender = "dev2@useb.co.kr"
    recipient = recipients
    subject = f"{word} Face Server API Usage"
    body_text = str(content)
    body_html = str(content)
    ses.send(sender, recipient, subject, body_text, body_html)

