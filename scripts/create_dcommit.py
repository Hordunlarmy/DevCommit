import os


def create_dcommit():
    dcommit_content = """
    # DevCommit configurations
LOCALE = en
MAX_NO = 1
COMMIT_TYPE = conventional
MODEL_NAME = gemini-1.5-flash
    """

    if "VIRTUAL_ENV" in os.environ:
        target_directory = os.path.join(
            os.environ.get("VIRTUAL_ENV", ""), "config"
        )
    else:
        target_directory = os.path.expanduser("~/")

    os.makedirs(target_directory, exist_ok=True)
    dcommit_file = os.path.join(target_directory, ".dcommit")

    with open(dcommit_file, "w") as file:
        file.write(dcommit_content.strip())
    print(f".dcommit file created at: {dcommit_file}")


if __name__ == "__main__":
    create_dcommit()
