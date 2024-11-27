import pytest
from unittest.mock import Mock, patch
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'code')))
import sendEmailStats

# from sendEmail import (
#     display_total,
#     send_email,
#     run,
#     process_email_input,
# )

# Fixtures for mock dependencies
@pytest.fixture
def bot_mock():
    return Mock()

@pytest.fixture
def helper_mock():
    with patch("sendEmailStats.helper") as helper:
        yield helper

@pytest.fixture
def graphing_mock():
    with patch("sendEmailStats.graphing") as graphing:
        yield graphing

@pytest.fixture
def smtp_mock():
    with patch("smtplib.SMTP") as smtp:
        yield smtp


# Test Cases

def test_send_email(smtp_mock):
    # Mock parameters
    user_email = "test@example.com"
    subject = "Test Subject"
    message = "This is a test email."
    attachment_path = "test_attachment.txt"

    # Create a temporary file as the attachment
    with open(attachment_path, "w") as f:
        f.write("This is a test attachment.")

    # Run the function
    sendEmailStats.send_email(user_email, subject, message, attachment_path)

    # Verify SMTP interactions
    smtp_mock.assert_called_with("smtp.gmail.com", 587)
    smtp_mock.return_value.starttls.assert_called_once()
    smtp_mock.return_value.login.assert_called_once_with("dollarbot123@gmail.com", "tsvueizeuvzivtjo")
    smtp_mock.return_value.sendmail.assert_called_once()
    smtp_mock.return_value.quit.assert_called_once()

    # Clean up
    os.remove(attachment_path)


def test_run(bot_mock):
    # Mock the message
    message_mock = Mock()
    message_mock.chat.id = 12345

    # Run the function
    sendEmailStats.run(message_mock, bot_mock)

    # Verify bot interactions
    bot_mock.send_message.assert_called_once_with(12345, "Please enter your email: ")
    bot_mock.register_next_step_handler.assert_called_once()


def test_process_email_input(bot_mock, helper_mock, graphing_mock):
    # Mock dependencies
    helper_mock.getSpendDisplayOptions.return_value = ["Day", "Month"]
    helper_mock.getUserHistory.return_value = [
        "2024-11-27,Food,50,USD",
        "2024-11-27,Transport,30,USD",
    ]
    helper_mock.get_user_preferred_currency.return_value = "USD"
    helper_mock.convert_currency.side_effect = lambda amount, currency, preferred: amount
    graphing_mock.visualize.return_value = "expenditure.png"

    # Mock message
    message_mock = Mock()
    message_mock.chat.id = 12345
    message_mock.text = "user@example.com"

    # Mock file existence
    with patch("os.path.isfile", return_value=True):
        sendEmailStats.process_email_input(message_mock, bot_mock)

    # Verify email sent
    bot_mock.send_message.assert_any_call(12345, "Email sent successfully!")
