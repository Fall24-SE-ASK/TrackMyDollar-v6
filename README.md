# 💰 TrackMyDollar V5.0 - Budget On The Go(BOTGo) 💰

![TrackMyDollar Project](https://github.com/Fall24-SE-ASK/TrackMyDollar-v6/blob/main/docs/mytrackmydollar.png)

![MIT license](https://img.shields.io/badge/License-MIT-green.svg)
[![Platform](https://img.shields.io/badge/Platform-Telegram-blue)](https://desktop.telegram.org/)
![GitHub](https://img.shields.io/badge/Language-Python-blue.svg)
[![GitHub contributors](https://img.shields.io/github/contributors/Fall24-SE-ASK/TrackMyDollar-v6)](https://github.com/Fall24-SE-ASK/TrackMyDollar-v6/graphs/contributors)
[![Test and Formatting](https://github.com/Fall24-SE-ASK/TrackMyDollar-v6/actions/workflows/test.yml/badge.svg)](https://github.com/Fall24-SE-ASK/TrackMyDollar-v6/actions/workflows/test.yml)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/ajith05/15d3ab1238848f946ed98c192fb45195/raw/coverage.json)](https://github.com/Fall24-SE-ASK/TrackMyDollar-v6/actions/workflows/test.yml)
[![Static Code Analysis](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/ajith05/c440db3fed64acd19235da2713aa8c7f/raw/Static_code_analysis.json)](https://github.com/Fall24-SE-ASK/TrackMyDollar-v6/actions/workflows/test.yml)
[![Security Scans](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/ajith05/3e60ee211c19e4f20d7c8bb5736f9361/raw/Security_scan.json)](https://github.com/Fall24-SE-ASK/TrackMyDollar-v6/actions/workflows/test.yml)


<!-- [![codecov](https://codecov.io/gh/sak007/MyDollarBot-BOTGo/branch/main/graph/badge.svg?token=5AYMR8MNMP)](https://codecov.io/gh/sak007/MyDollarBot-BOTGo) -->
[![GitHub issues](https://img.shields.io/github/issues/Fall24-SE-ASK/TrackMyDollar-v6)](https://github.com/Fall24-SE-ASK/TrackMyDollar-v6/issues)
![Fork](https://img.shields.io/github/forks/anuj672/MyDollarBot-BOTGo)

<hr>

## About TrackMyDollar

TrackMyDollar is an easy-to-use Telegram Bot that assists you in recording your daily expenses on a local system without any hassle 
With simple commands, this bot allows you to:
- Add/Record a new spending
- Show the sum of your expenditure for the current day/month
- Display your spending history
- Clear/Erase all your records
- Edit/Change any spending details if you wish to
- Add a recurring expense 
- User can add a new category and delete an existing category 
- User can see the budget value for the total expense 
- Added pie charts, bar graphs with and without budget lines 
- Deployment on GCP 

## What's new? (From Phase 4 to Phase 5)

- Calendar Feature: Allows users to select dates for their transactions directly via a calendar interface.
- Income Feature: Tracks income in addition to expenses, allowing better financial planning.
- Multi-Currency Feature: Supports tracking expenses and income in different currencies.
- Improved Test Cases and new badges: Added more robust test cases for increased coverage and Added badges for coverage, static code analysis and Security scans.
- Automated Static Code Analysis & Security Scans: Integrates automatic static code analysis and security scans with GitHub Actions, ensuring code quality.


## What more can be done?
Check out the issue list [here](https://github.com/Fall24-SE-ASK/TrackMyDollar-v6/issues) to see what more can be done to make MyDollarBot better. 

## Demo

[![Watch the Demo](https://img.youtube.com/vi/LZnSmxAyVUo/0.jpg)](https://www.youtube.com/watch?v=LZnSmxAyVUo)

## Installation and Quick Start guide

The below instructions can be followed in order to set-up this bot at your end in a span of few minutes! Let's get started:

1. Clone this repository to your local system.

2. In Telegram, search for "BotFather". Click on "Start", and enter the following command:
```
  /newbot
```
Follow the instructions on screen and choose a name for your bot. After this, select a username for your bot that ends with "bot".

3. BotFather will now confirm the creation of your bot and provide a TOKEN to access the HTTP API - copy and save this token for future use.

4. Copy the token provided by the bot and add/replace it in the user.properties file (in the format api_token=<your_token>).

5. Install [docker desktop](https://docs.docker.com/desktop/) or [docker engine](https://docs.docker.com/engine/) in your local system if you don't already have it installed

6. In the directory where this repo has been cloned, please run the below command to build a docker image, run it as container and see its logs:
```
   docker compose up -d
   docker compose logs bot -f
```

A successful run will generate a message on your terminal that says "TeleBot: Started polling." 

7. In the Telegram app, search for your newly created bot by entering the username and open the same. Now, on Telegram, enter the "/start" or "/menu" command, and you are all set to track your expenses!

Note: To stop the bot, run `docker compose down` in the repo directory.

## Usage
Here’s an overview of some key commands:

- Add Expense: /add <amount> <category> <description>
- View Daily Summary: /day
- View Monthly Summary: /month
- Edit/Delete Expense: /edit <id> or /delete <id>
- Set Recurring Expense: /recurring <amount> <category>
- Show Pie Chart: /chart
- Set Budget: /budget <amount>

## Testing

We use pytest to perform testing on all unit tests together. The command needs to be run from the home directory of the project. The command is:
```
python -m pytest test/
```

## Code Coverage

Code coverage is part of the build. Every time new code is pushed to the repository, the build is run, and along with it, code coverage is computed. This can be viewed by selecting the build, and then choosing the codecov pop-up on hover.

Locally, we use the coverage package in python for code coverage. The commands to check code coverage in python are as follows:

```
coverage run -m pytest test/
coverage report
```

Please note: A coverage below 70% will cause the build to fail.

## Who Should Use TrackMyDollar?
TrackMyDollar is designed for anyone looking for a simple, effective way to track daily expenses and manage personal finances. It’s ideal for:

- Individuals who want a lightweight solution to monitor their spending habits without complicated setups.
- Budget-Conscious Users seeking a tool to record income and expenses, visualize their spending, and set budgets.
- Travelers or freelancers who need multi-currency support for tracking expenses in various currencies.
- Tech-Savvy Users familiar with messaging apps like Telegram who prefer quick, command-based interactions for managing finances.
- Whether you are a student, working professional, or someone simply wanting to take control of your finances, TrackMyDollar provides an easy-to-use platform to simplify financial tracking.

## Troubleshooting

- Invalid Bot Token: If your bot doesn’t start, confirm the token in user.properties is correct. Regenerate it in BotFather if necessary.
- Dependency Errors: Run pip install -r requirements.txt again to ensure all packages are correctly installed.
- Run Script Permission Issues: On macOS/Linux, make the script executable with chmod +x run.sh.
- Network/Connection Errors: Verify internet connection and ensure Telegram access in your region.

## Contributing
Contributions are welcome! Please read the CONTRIBUTING.md for more details.

- Fork the repository and create a new branch.
- Submit a pull request with a description of changes.
- Test Coverage: Ensure changes pass all tests and maintain 70%+ coverage.

## License
- This project is licensed under the MIT License. See the LICENSE file for details.

## Notes:
You can download and install the Telegram desktop application for your system from the following site: https://desktop.telegram.org/

## Authors (Iteration 6)
- Ajith Kanumuri
- Suhas Adidela
- Venkata Krishna Mangapuram
  
<hr>
<p>Title:'Track My Dollar'</p>
<p>Version: '6.0'</p>
<p>Description: 'An easy to use Telegram Bot to track everyday expenses'</p>
<p>Authors(Iteration 5):'Sainath, Mona, Vishal'</p>
<p>Authors(Iteration 4):'Anuj, Bhavesh, Jash, Vaibhavi'</p>
<p>Authors(Iteration 3):'Vraj, Alex, Leo, Prithvish, Seeya'</p>
<p>Authors(Iteration 2):'Athithya, Subramanian, Ashok, Zunaid, Rithik'</p>
<p>Authors(Iteration 1):'Dev, Prakruthi, Radhika, Rohan, Sunidhi'</p>
