import csv


class RowCleaner:
    def __init__(self):
        self.rows = []
        self.prev_type = ""
        self.header = []
        self.cols_to_remove = [
            'Outfit ideas',
            'Other'
        ]
        self.free_id = 0

    def load_rows(self, csv_reader):
        self.header = self._clean_header(next(csv_reader))
        self.header[0] = 'Id'
        RowCleaner._clean_header(self.header)

        for row in csv_reader:
            clean_row = self.handle_row(row)
            if clean_row:
                self.rows.append(clean_row)

        for col in self.cols_to_remove:
            self.header.pop(self.header.index(col))

    @staticmethod
    def _clean_header(row):
        # Strips leading/trailing whitespaces from row
        header = []
        for field in row:
            header.append(field.strip())
        return header

    @staticmethod
    def _row_empty(row):
        nonempty = 0
        for item in row:
            if item:
                nonempty += 1
                if nonempty > 1:
                    return False
        return True

    @staticmethod
    def _clean_styles(styles):
        clean_styles = []
        for style in styles.split(","):
            clean_styles.append(style.strip().capitalize())
        return ", ".join(clean_styles)

    def _make_id(self):
        self.free_id += 1
        return self.free_id - 1

    def handle_row(self, row):
        if RowCleaner._row_empty(row):
            return None  # Ignore empty rows
        row[0] = self._make_id()

        # Fill in missing Type
        if row[1]:
            self.prev_type = row[1]
        else:
            row[1] = self.prev_type

        # Convert strike x's to int
        strikes_field = row[self.header.index('Sexy check?')]
        row[self.header.index('Sexy check?')] = RowCleaner.sexy_to_int(strikes_field)

        # Clean style
        row[self.header.index('Style')] = RowCleaner._clean_styles(row[self.header.index('Style')])

        # Remove columns that are not desired
        remove_indices = []
        for col in self.cols_to_remove:  # first find indices of cols meant to be removed
            remove_indices.append(self.header.index(col))
        remove_indices.sort(reverse=True)  # this is important to delete them lowest first!
        for remove_index in remove_indices:
            row.pop(remove_index)

        # Strip leading/trailing spaces
        for field in row:
            if type(field) == str:
                field.strip()

        # print(row)
        return row

    @staticmethod
    def sexy_to_int(field):
        return field.count('x')

    def get_rows(self):
        return self.rows

    def write_to_file(self, file):
        writer = csv.writer(file)
        writer.writerow(self.header)
        writer.writerows(self.rows)


def main():
    cleaner = RowCleaner()
    with open('clothes.csv', 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        cleaner.load_rows(csv_reader)

    with open('items.csv', 'w', encoding='utf-8', newline='') as output_file:
        cleaner.write_to_file(output_file)
    

if __name__ == '__main__':
    main()
