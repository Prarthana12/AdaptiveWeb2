import csv
from pathlib import Path


class ReadCsv:


    def read_csv(self, fileName):
        with open('query.csv', mode='r') as file:
            reader = csv.DictReader(file)
            line_count = 0
            for row in reader:
                if(line_count == 0):
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                print(f'\t{row["type"]} \n {row["text"]} \n {row["code"]}.')
                line_count += 1
            print(f'Processed {line_count} lines.')


if __name__ == "__main__":
    r = ReadCsv()
    fileName = Path("query.csv")
    r.read_csv(fileName)
