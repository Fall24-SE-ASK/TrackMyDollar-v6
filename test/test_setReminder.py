import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

import sys
from pathlib import Path
import os
from apscheduler.triggers.date import DateTrigger



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'code')))
import setReminder
# from setReminder import run_set_reminder, send_reminder



@pytest.fixture
def bot_mock():
    """Mock object for the bot."""
    return Mock()


@pytest.fixture
def scheduler_mock():
    """Mock object for the scheduler."""
    return Mock()


def test_run_set_reminder_valid(bot_mock, scheduler_mock):
    # Mocking a valid message object
    message_mock = Mock()
    future_time = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d-%H:%M")
    message_mock.text = f"/remind {future_time} Groceries"
    message_mock.chat.id = 12345
    future_time_in_id = datetime.strptime(future_time, "%Y-%m-%d-%H:%M").strftime("%Y-%m-%d %H:%M:%S")
    expected_id = f'reminder_{message_mock.chat.id}_{future_time_in_id}'

    # Mock the DateTrigger object
    with patch("setReminder.DateTrigger") as DateTriggerMock:
        trigger_instance = Mock()
        DateTriggerMock.return_value = trigger_instance

        with patch("setReminder.scheduler", scheduler_mock):
            setReminder.run_set_reminder(message_mock, bot_mock)

            # Verify the trigger instance was passed correctly
            scheduler_mock.add_job.assert_called_once_with(
                func=setReminder.send_reminder,
                trigger=trigger_instance,
                args=[12345, "Groceries", bot_mock],
                id=expected_id,
                replace_existing=True,
            )


def test_run_set_reminder_invalid_format(bot_mock):
    """Test when an invalid reminder format is provided."""
    # Mocking an invalid message object
    message_mock = Mock()
    message_mock.text = "/remind invalid-format"
    message_mock.chat.id = 12345

    setReminder.run_set_reminder(message_mock, bot_mock)

    # Verify the bot sent an error message
    bot_mock.reply_to.assert_called_once_with(
        message_mock, "Invalid format! Use /remind YYYY-MM-DD-HH:MM (24-hour format)."
    )


def test_run_set_reminder_past_time(bot_mock):
    """Test setting a reminder in the past."""
    # Mocking a message with a past datetime
    past_time = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d-%H:%M")
    message_mock = Mock()
    message_mock.text = f"/remind {past_time} Past reminder"
    message_mock.chat.id = 12345

    setReminder.run_set_reminder(message_mock, bot_mock)

    # Verify the bot sent an error message
    bot_mock.reply_to.assert_called_once_with(
        message_mock, "You cannot set a reminder in the past, please set a later time"
    )


def test_send_reminder(bot_mock):
    """Test sending a reminder."""
    chat_id = 12345
    reminder_message = "Don't forget to check your email"

    setReminder.send_reminder(chat_id, reminder_message, bot_mock)

    # Verify the bot sent the correct reminder message
    bot_mock.send_message.assert_called_once_with(chat_id, f"Reminder: {reminder_message}")
