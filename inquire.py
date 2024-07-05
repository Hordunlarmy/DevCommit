from InquirerPy import inquirer

name = inquirer.text(message="What's your name:").execute()
fav_lang = inquirer.select(
    message="What's your favourite programming language:",
    choices=["Go", "Python", "Rust", "JavaScript"],
).execute()
confirm = inquirer.confirm(message="Confirm?").execute()
