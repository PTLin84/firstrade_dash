from pdfminer.high_level import extract_text
import os

directory_path = '/mnt/c/Users/Kyle/GoogleDrive/firstrade/statements'
target_page = 0


def main():

    # Get all filenames in the directory
    filenames = [file.split('.')[0] for file in os.listdir(
        directory_path) if "pdf" in file]
    print(filenames)

    for filename in filenames:
        text = extract_text(os.path.join(directory_path, filename +
                            '.pdf'), page_numbers=[target_page])
        ind = text.find("Total Equity Holdings")
        start_bal, end_bal = text[ind:ind+50].replace('\n\n', ' ').split()[3:5]
        print(
            f'{filename}: Starting balance:{start_bal:>11} | Ending balance:{end_bal:>11}')


def get_all_balances():
    """Get all balances.

    Returns:
        balances(dict): {"202309": [starting_balance, ending_balance]}
    """
    balances = dict()
    filenames = [file.split('.')[0] for file in os.listdir(
        directory_path) if "pdf" in file]

    for filename in filenames:
        text = extract_text(os.path.join(directory_path, filename) +
                            '.pdf', page_numbers=[target_page])
        ind = text.find("Total Equity Holdings")
        start_bal, end_bal = text[ind:ind+50].replace('\n\n', ' ').split()[3:5]
        year_month = filename[:4] + '-' + filename[-2:]  # YYYY-MM
        balances[year_month] = [start_bal, end_bal]

    return balances


if __name__ == "__main__":
    main()
